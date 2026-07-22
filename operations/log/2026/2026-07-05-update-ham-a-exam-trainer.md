---
date: 2026-07-05
operator: ai
affected: [n100, ham-a-exam-trainer]
risk: low
status: success
guardrails: [CONFIRM, PRE-04]
---

# 更新 Ham-A-Exam-Trainer 静态站点（20260705-214009）

## 目的
本地 Ham-A-Exam-Trainer 有新版本，需要继续发布到 n100 现有静态站点。

## 执行
使用已沉淀的部署脚本：

```bash
scripts/deploy-ham-a-exam-trainer.sh
```

实际 release：

```text
20260705-214009
```

脚本执行的关键动作：
- 上传本地静态文件到 `/home/johnson/sites/ham-a-exam-trainer/www.next-20260705-214009`。
- 将当前 `www` 改名为 `www.backup-20260705-214009`。
- 将 `www.next-20260705-214009` 切换为新的 `www`。
- 重启 `ham-a-exam-trainer` 容器。
- 验证内网后端与 `ham.jsho.top`。

未修改 NPM、AdGuardHome、DNS、主路由或公网入口。

## 验证
上传后的关键文件大小：

```text
index.html 19612 bytes
app.js 86374 bytes
styles.css 28545 bytes
data/explanations.js 314036 bytes
data/knowledge.js 719114 bytes
data/questions.js 598621 bytes
assets/knowledge/K4-21.png 1284516 bytes
```

本次新增/包含的知识点相关内容：

```text
data/knowledge-legacy.js
knowledge/1-法规与管理.md
knowledge/2-通联操作与术语.md
knowledge/3-设备天线与传播.md
knowledge/4-电学基础与测量.md
knowledge/5-发射指标与安全.md
knowledge/_知识点工程总览.md
scripts/build_knowledge_data.js
scripts/generate_knowledge_image.py
```

容器状态：

```text
ham-a-exam-trainer Up ... 0.0.0.0:18080->18080/tcp
```

内网后端验证：

```text
internal-index        http=200 size=19612  content_type=text/html
internal-app          http=200 size=86374  content_type=application/javascript
internal-styles       http=200 size=28545  content_type=text/css
internal-explanations http=200 size=314036 content_type=application/javascript
internal-knowledge    http=200 size=719114 content_type=application/javascript
internal-route        http=200 size=19612  content_type=text/html
```

NPM 域名验证：

```text
domain-index        http=200 size=19612  content_type=text/html
domain-app          http=200 size=86374  content_type=application/javascript
domain-explanations http=200 size=314036 content_type=application/javascript
domain-knowledge    http=200 size=719114 content_type=application/javascript
```

发布后目录：

```text
/home/johnson/sites/ham-a-exam-trainer/www
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260702-114908
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260702-161851
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260702-225749
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260704-002336
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260705-214009
/home/johnson/sites/ham-a-exam-trainer/www.failed-20260704-002248-upload
```

## 回滚
保留了上一版目录，可通过目录切换回滚。只影响 `ham-a-exam-trainer` 容器：

```bash
ssh -o BatchMode=yes n100 '
  base=/home/johnson/sites/ham-a-exam-trainer
  mv "$base/www" "$base/www.failed-20260705-214009"
  mv "$base/www.backup-20260705-214009" "$base/www"
  docker restart ham-a-exam-trainer
'
```

上述回滚不删除文件；如需清理 `www.failed-*` 或旧备份目录，需单独确认目录范围。

## 影响
- n100 上 `ham-a-exam-trainer` 静态内容已更新到 release `20260705-214009`。
- `ham-a-exam-trainer` 容器重启一次，短暂中断该站点。
- `inventory/services.md` 已更新溯源。

## 后续
- 如确认多版备份稳定无用，可后续人工确认后清理旧备份目录。
