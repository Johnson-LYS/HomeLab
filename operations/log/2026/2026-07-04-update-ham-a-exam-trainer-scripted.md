---
date: 2026-07-04
operator: ai
affected: [n100, ham-a-exam-trainer]
risk: low
status: success
guardrails: [CONFIRM, PRE-04]
---

# 脚本化更新 Ham-A-Exam-Trainer 静态站点（20260704-002336）

## 目的
本地 Ham-A-Exam-Trainer 再次更新。由于发布流程已经固定，将流程沉淀成脚本并用脚本发布新版本。

## 执行
新增脚本：

```text
scripts/deploy-ham-a-exam-trainer.sh
```

脚本默认参数：

```text
SOURCE_DIR=/Users/liyongsheng/Library/Mobile Documents/iCloud~md~obsidian/Documents/CyberNote/Projects/Ham-A-Exam-Trainer
REMOTE_HOST=n100
REMOTE_BASE=/home/johnson/sites/ham-a-exam-trainer
INTERNAL_ORIGIN=http://192.168.8.15:18080
PUBLIC_ORIGIN=https://ham.jsho.top
```

执行：

```bash
scripts/deploy-ham-a-exam-trainer.sh
```

实际 release：

```text
20260704-002336
```

脚本执行的关键动作：
- 上传本地静态文件到 `/home/johnson/sites/ham-a-exam-trainer/www.next-20260704-002336`。
- 将当前 `www` 改名为 `www.backup-20260704-002336`。
- 将 `www.next-20260704-002336` 切换为新的 `www`。
- 重启 `ham-a-exam-trainer` 容器。
- 验证内网后端与 `ham.jsho.top`。

中间修正：
- 第一次脚本运行暴露远端 `tar` 参数传递问题，尚未切换 `www`，线上站点未受影响。
- 修复脚本后，将失败暂存目录改名保留为 `www.failed-20260704-002248-upload`，未删除任何目录。

发布后目录：

```text
/home/johnson/sites/ham-a-exam-trainer/www
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260702-114908
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260702-161851
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260702-225749
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260704-002336
/home/johnson/sites/ham-a-exam-trainer/www.failed-20260704-002248-upload
```

## 验证
上传后的文件大小：

```text
index.html 19612 bytes
app.js 85499 bytes
styles.css 28365 bytes
data/explanations.js 314036 bytes
data/knowledge.js 33705 bytes
data/questions.js 598621 bytes
```

容器状态：

```text
ham-a-exam-trainer Up ... 0.0.0.0:18080->18080/tcp
```

内网后端验证：

```text
internal-index        http=200 size=19612  content_type=text/html
internal-app          http=200 size=85499  content_type=application/javascript
internal-styles       http=200 size=28365  content_type=text/css
internal-explanations http=200 size=314036 content_type=application/javascript
internal-knowledge    http=200 size=33705  content_type=application/javascript
internal-route        http=200 size=19612  content_type=text/html
```

NPM 域名验证：

```text
domain-index        http=200 size=19612  content_type=text/html
domain-app          http=200 size=85499  content_type=application/javascript
domain-explanations http=200 size=314036 content_type=application/javascript
domain-knowledge    http=200 size=33705  content_type=application/javascript
```

## 回滚
保留了上一版目录，可通过目录切换回滚。只影响 `ham-a-exam-trainer` 容器：

```bash
ssh -o BatchMode=yes n100 '
  base=/home/johnson/sites/ham-a-exam-trainer
  mv "$base/www" "$base/www.failed-20260704-002336"
  mv "$base/www.backup-20260704-002336" "$base/www"
  docker restart ham-a-exam-trainer
'
```

上述回滚不删除文件；如需清理 `www.failed-*` 或旧备份目录，需单独确认目录范围。

## 影响
- n100 上 `ham-a-exam-trainer` 静态内容已更新到 release `20260704-002336`。
- `ham-a-exam-trainer` 容器重启一次，短暂中断该站点。
- 新增可复用部署脚本 `scripts/deploy-ham-a-exam-trainer.sh`。
- `inventory/services.md` 已更新溯源。

## 后续
- 如确认多版备份稳定无用，可后续人工确认后清理旧备份目录。
