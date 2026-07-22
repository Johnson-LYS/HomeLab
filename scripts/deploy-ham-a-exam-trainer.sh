#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${SOURCE_DIR:-/Users/liyongsheng/Library/Mobile Documents/iCloud~md~obsidian/Documents/CyberNote/Projects/Ham-A-Exam-Trainer}"
REMOTE_HOST="${REMOTE_HOST:-n100}"
REMOTE_BASE="${REMOTE_BASE:-/home/johnson/sites/ham-a-exam-trainer}"
RELEASE_ID="${RELEASE_ID:-$(date +%Y%m%d-%H%M%S)}"
INTERNAL_ORIGIN="${INTERNAL_ORIGIN:-http://192.168.8.15:18080}"
PUBLIC_ORIGIN="${PUBLIC_ORIGIN:-https://ham.jsho.top}"

SSH_OPTS=(-o BatchMode=yes)
REQUIRED_FILES=(
  index.html
  styles.css
  app.js
  data/questions.js
)

log() {
  printf '[deploy-ham] %s\n' "$*"
}

remote_sh() {
  ssh "${SSH_OPTS[@]}" "$REMOTE_HOST" 'sh -s' -- "$@"
}

fetch_check() {
  local label="$1"
  local url="$2"
  local out="/tmp/ham-a-${RELEASE_ID}-${label}"

  curl --http1.1 --no-keepalive --max-time 10 -fsS \
    -o "$out" \
    -w "${label} http=%{http_code} size=%{size_download} content_type=%{content_type}\n" \
    "$url"
}

log "release=${RELEASE_ID}"
log "source=${SOURCE_DIR}"
log "remote=${REMOTE_HOST}:${REMOTE_BASE}"

if [[ ! -d "$SOURCE_DIR" ]]; then
  printf 'source directory not found: %s\n' "$SOURCE_DIR" >&2
  exit 1
fi

for file in "${REQUIRED_FILES[@]}"; do
  if [[ ! -f "$SOURCE_DIR/$file" ]]; then
    printf 'required file missing: %s\n' "$SOURCE_DIR/$file" >&2
    exit 1
  fi
done

log "checking remote container and directories"
remote_sh "$REMOTE_BASE" "$RELEASE_ID" <<'REMOTE'
set -eu
base=$1
release=$2

docker ps --filter name='^/ham-a-exam-trainer$' --format '{{.Names}} {{.Status}} {{.Ports}}'
test -d "$base/www"
test ! -e "$base/www.next-$release"
test ! -e "$base/www.backup-$release"
mkdir -p "$base/www.next-$release"
REMOTE

log "uploading files"
remote_next="${REMOTE_BASE}/www.next-${RELEASE_ID}"
remote_next_q="$(printf '%q' "$remote_next")"
COPYFILE_DISABLE=1 tar --no-xattrs --exclude .DS_Store --exclude '._*' \
  -C "$SOURCE_DIR" -cf - . \
  | ssh "${SSH_OPTS[@]}" "$REMOTE_HOST" "tar -C $remote_next_q -xf -"

log "uploaded files"
ssh "${SSH_OPTS[@]}" "$REMOTE_HOST" \
  "find $remote_next_q -maxdepth 3 -type f -printf '%P %s bytes\n' | sort"

log "switching release"
remote_sh "$REMOTE_BASE" "$RELEASE_ID" <<'REMOTE'
set -eu
base=$1
release=$2

test -d "$base/www"
test -d "$base/www.next-$release"
test ! -e "$base/www.backup-$release"

mv "$base/www" "$base/www.backup-$release"
mv "$base/www.next-$release" "$base/www"
docker restart ham-a-exam-trainer >/dev/null
sleep 1
docker ps --filter name='^/ham-a-exam-trainer$' --format '{{.Names}} {{.Status}} {{.Ports}}'
find "$base" -maxdepth 1 -type d -printf "%f\n" | sort
REMOTE

log "verifying internal origin"
fetch_check internal-index "${INTERNAL_ORIGIN}/"
fetch_check internal-app "${INTERNAL_ORIGIN}/app.js"
fetch_check internal-styles "${INTERNAL_ORIGIN}/styles.css"
fetch_check internal-explanations "${INTERNAL_ORIGIN}/data/explanations.js"
fetch_check internal-knowledge "${INTERNAL_ORIGIN}/data/knowledge.js"
fetch_check internal-route "${INTERNAL_ORIGIN}/practice"

log "verifying public origin"
fetch_check domain-index "${PUBLIC_ORIGIN}/"
fetch_check domain-app "${PUBLIC_ORIGIN}/app.js"
fetch_check domain-explanations "${PUBLIC_ORIGIN}/data/explanations.js"
fetch_check domain-knowledge "${PUBLIC_ORIGIN}/data/knowledge.js"

log "done release=${RELEASE_ID}"
