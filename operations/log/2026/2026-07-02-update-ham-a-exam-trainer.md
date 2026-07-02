---
date: 2026-07-02
operator: ai
affected: [n100, ham-a-exam-trainer]
risk: low
status: success
guardrails: [CONFIRM, PRE-04]
---

# 更新 Ham-A-Exam-Trainer 静态站点

## 目的
本地项目 `/Users/liyongsheng/Library/Mobile Documents/iCloud~md~obsidian/Documents/CyberNote/Projects/Ham-A-Exam-Trainer` 有变更，需要同步到 n100 已部署的静态站点。

## 执行
未修改 NPM、AdGuardHome、DNS、主路由或公网入口。仍使用现有端口 `18080` 和现有容器 `ham-a-exam-trainer`。

本次使用新目录上传后切换，旧版本保留为备份：

```text
/home/johnson/sites/ham-a-exam-trainer/www                 # 新版本
/home/johnson/sites/ham-a-exam-trainer/www.backup-20260702-114908
```

关键步骤：

```bash
ssh -o BatchMode=yes n100 'mkdir -p /home/johnson/sites/ham-a-exam-trainer/www.next-20260702-114908'

COPYFILE_DISABLE=1 tar --no-xattrs --exclude .DS_Store --exclude '._*' \
  -C '<local Ham-A-Exam-Trainer>' -cf - . \
  | ssh -o BatchMode=yes n100 \
      'tar -C /home/johnson/sites/ham-a-exam-trainer/www.next-20260702-114908 -xf -'

ssh -o BatchMode=yes n100 '
  base=/home/johnson/sites/ham-a-exam-trainer
  ts=20260702-114908
  mv "$base/www" "$base/www.backup-$ts"
  mv "$base/www.next-$ts" "$base/www"
  docker restart ham-a-exam-trainer
'
```

本次本地新增/更新的主要文件包括：
- `index.html`
- `styles.css`
- `app.js`
- `data/knowledge.js`
- `data/explanations.js`
- `data/explanations/*.json`
- `scripts/build_explanations.js`

## 验证
容器状态：

```text
ham-a-exam-trainer Up ... 0.0.0.0:18080->18080/tcp
```

内网后端验证：

```text
index        http=200 size=15813  content_type=text/html
app.js       http=200 size=68336  content_type=application/javascript
styles.css   http=200 size=22483  content_type=text/css
explanations http=200 size=314036 content_type=application/javascript
knowledge    http=200 size=33705  content_type=application/javascript
```

NPM 域名验证：

```text
https://ham.jsho.top/                    http=200 size=15813
https://ham.jsho.top/data/explanations.js http=200 size=314036
```

## 回滚
保留了上一版目录，可通过目录切换回滚。只影响 `ham-a-exam-trainer` 容器：

```bash
ssh -o BatchMode=yes n100 '
  base=/home/johnson/sites/ham-a-exam-trainer
  mv "$base/www" "$base/www.failed-20260702-114908"
  mv "$base/www.backup-20260702-114908" "$base/www"
  docker restart ham-a-exam-trainer
'
```

上述回滚不删除文件；如需清理 `www.failed-*` 或旧备份目录，需单独确认目录范围。

## 影响
- n100 上 `ham-a-exam-trainer` 静态内容已更新。
- `ham-a-exam-trainer` 容器重启一次，短暂中断该站点。
- `inventory/services.md` 已更新核实时间与来源。

## 后续
- 如确认新版稳定，可后续人工确认后清理旧备份目录。
