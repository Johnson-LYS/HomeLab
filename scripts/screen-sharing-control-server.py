#!/usr/bin/env python3
"""Small authenticated HTTP service for closing macOS Screen Sharing."""

from __future__ import annotations

import hmac
import json
import os
import subprocess
import sys
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional


HOST = os.environ.get("HOMELAB_SCREEN_SHARING_HOST", "192.168.8.18")
PORT = int(os.environ.get("HOMELAB_SCREEN_SHARING_PORT", "18765"))
TOKEN_FILE = Path(
    os.environ.get(
        "HOMELAB_SCREEN_SHARING_TOKEN_FILE",
        str(Path.home() / "Library/Application Support/HomeLabScreenSharingControl/token"),
    )
)


def load_token() -> str:
    try:
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise SystemExit(f"token file not found: {TOKEN_FILE}") from None
    if len(token) < 32:
        raise SystemExit("token is too short")
    return token


TOKEN = load_token()


def run_command(args: list[str], timeout: float = 5.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def screen_sharing_pids() -> list[int]:
    result = run_command(["/usr/bin/pgrep", "-x", "Screen Sharing"])
    if result.returncode != 0:
        return []
    pids: list[int] = []
    for line in result.stdout.splitlines():
        try:
            pids.append(int(line.strip()))
        except ValueError:
            continue
    return pids


def wait_until_closed(timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not screen_sharing_pids():
            return True
        time.sleep(0.2)
    return not screen_sharing_pids()


def close_screen_sharing() -> dict[str, object]:
    before = screen_sharing_pids()
    methods: list[str] = []

    if before:
        osa = run_command(
            [
                "/usr/bin/osascript",
                "-e",
                'tell application id "com.apple.ScreenSharing" to quit',
            ]
        )
        methods.append(f"osascript:{osa.returncode}")

        if not wait_until_closed(3.0):
            pkill = run_command(["/usr/bin/pkill", "-TERM", "-x", "Screen Sharing"])
            methods.append(f"pkill-term:{pkill.returncode}")
            wait_until_closed(3.0)

    after = screen_sharing_pids()
    return {
        "ok": not after,
        "before_running": bool(before),
        "after_running": bool(after),
        "before_pids": before,
        "after_pids": after,
        "methods": methods,
    }


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


class Handler(BaseHTTPRequestHandler):
    server_version = "HomeLabScreenSharingControl/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stdout.write(f"{now()} {self.client_address[0]} {fmt % args}\n")
        sys.stdout.flush()

    def send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def authorized(self) -> bool:
        auth = self.headers.get("Authorization", "")
        token = ""
        if auth.startswith("Bearer "):
            token = auth.removeprefix("Bearer ").strip()
        else:
            token = self.headers.get("X-HomeLab-Token", "").strip()
        return hmac.compare_digest(token, TOKEN)

    def require_auth(self) -> bool:
        if self.authorized():
            return True
        self.send_json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
        return False

    def do_GET(self) -> None:
        if self.path != "/health":
            self.send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
            return
        if not self.require_auth():
            return
        self.send_json(
            HTTPStatus.OK,
            {"ok": True, "screen_sharing_running": bool(screen_sharing_pids())},
        )

    def do_POST(self) -> None:
        if self.path != "/close-screen-sharing":
            self.send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
            return
        if not self.require_auth():
            return
        self.send_json(HTTPStatus.OK, close_screen_sharing())


class Server(ThreadingHTTPServer):
    allow_reuse_address = True


def main() -> int:
    last_error: Optional[OSError] = None
    for _ in range(12):
        try:
            server = Server((HOST, PORT), Handler)
            break
        except OSError as exc:
            last_error = exc
            print(f"{now()} bind failed on {HOST}:{PORT}: {exc}; retrying", flush=True)
            time.sleep(5)
    else:
        print(f"{now()} unable to bind {HOST}:{PORT}: {last_error}", file=sys.stderr)
        return 1

    print(f"{now()} listening on {HOST}:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
