---
date: 2026-07-02
operator: ai
affected: [n100, ham-a-exam-trainer]
risk: low
status: success
guardrails: [CONFIRM, PRE-04]
---

# 更新 Ham-A-Exam-Trainer 静态站点（20260702-225749）

## 目的
本地 Ham-A-Exam-Trainer 再次更新，需要发布到 n100 的现有静态站点，并保留上一版目录以便回滚。

## 执行
未修改 NPM、AdGuardHome、DNS、主路由或公网入口。仍使用现有端口 `18080` 和现有容器 `ham-a-exam-trainer`。

新发布目录：

```text
/home/johnson/sites/ham-a-exam-trainer/www.next-20260702-225749
```

关键步骤：

```bash
ssh -o BatchMode=yes n100 \
  'mkdir -p /home/johnson/sites/ham-a-exam-trainer/www.next-20260702-225749'

COPYFILE_DISABLE=1 tar --no-xattrs --exclude .DS_Store --exclude '._*' \
  -C '<local Ham-A-Exam-Trainer>' -cf - . \
  | ssh -o BatchMode=yes n100 \
      'tar -C /home/johnson/sites/ham-a-exam-trainer/www.next-20260702-225749 -xf -'

ssh -o BatchMode=yes n100 '
  base=/home/johnson/sites/ham-a-exam-trainer
  ts=20260702-225749
  mv "$base/www" "$base/www.backup-$ts"
  mv "$base/www.next-$ts" "$base/www"
  docker restart ham-a-exam-trainer
'
```

发布后目录：

```text
/home/johnson/sites/ham-a-exam-trainer/www
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260702-114908
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260702-161851
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260702-225749
```

## 验证
容器状态：

```text
ham-a-exam-trainer Up ... 0.0.0.0:18080->18080/tcp
```

内网后端验证：

```text
http://192.168.8.15:18080/                     http=200 size=19516  content_type=text/html
http://192.168.8.15:18080/app.js               http=200 size=84524  content_type=application/javascript
http://192.168.8.15:18080/styles.css           http=200 size=28365  content_type=text/css
http://192.168.8.15:18080/data/explanations.js http=200 size=314036 content_type=application/javascript
http://192.168.8.15:18080/data/knowledge.js    http=200 size=33705  content_type=application/javascript
http://192.168.8.15:18080/practice             http=200 size=19516  content_type=text/html
```

NPM 域名验证：

```text
https://ham.jsho.top/                     http=200 size=19516  content_type=text/html
https://ham.jsho.top/app.js               http=200 size=84524  content_type=application/javascript
https://ham.jsho.top/data/explanations.js http=200 size=314036 content_type=application/javascript
https://ham.jsho.top/data/knowledge.js    http=200 size=33705  content_type=application/javascript
```

## 回滚
保留了上一版目录，可通过目录切换回滚。只影响 `ham-a-exam-trainer` 容器：

```bash
ssh -o BatchMode=yes n100 '
  base=/home/johnson/sites/ham-a-exam-trainer
  mv "$base/www" "$base/www.failed-20260702-225749"
  mv "$base/www.backup-20260702-225749" "$base/www"
  docker restart ham-a-exam-trainer
'
```

上述回滚不删除文件；如需清理 `www.failed-*` 或旧备份目录，需单独确认目录范围。

## 影响
- n100 上 `ham-a-exam-trainer` 静态内容已更新到 release `20260702-225749`。
- `ham-a-exam-trainer` 容器重启一次，短暂中断该站点。
- `inventory/services.md` 已更新溯源。

## 后续
- 如确认新版稳定，可后续人工确认后清理旧备份目录。
