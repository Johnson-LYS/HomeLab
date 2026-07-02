---
date: 2026-06-30
operator: ai
affected: [n100, ham-a-exam-trainer]
risk: low
status: success
guardrails: [CONFIRM]
---

# 部署 Ham-A-Exam-Trainer 静态站点

## 目的
把本地静态网页 `/Users/liyongsheng/Library/Mobile Documents/iCloud~md~obsidian/Documents/CyberNote/Projects/Ham-A-Exam-Trainer` 部署到 n100，作为 NPM 后端服务使用。

## 执行
只读确认端口占用后选择宿主端口 `18080`，未修改 NPM、AdGuardHome、主路由或公网入口。

部署目录：

```bash
/home/johnson/sites/ham-a-exam-trainer/
├── nginx.conf
└── www/
```

同步文件：

```bash
ssh n100 'mkdir -p /home/johnson/sites/ham-a-exam-trainer/www'
tar --exclude .DS_Store -C '<local Ham-A-Exam-Trainer>' -cf - . \
  | ssh n100 'tar -C /home/johnson/sites/ham-a-exam-trainer/www -xf -'
ssh n100 'find /home/johnson/sites/ham-a-exam-trainer/www -type f \( -name "._*" -o -name ".DS_Store" \) -delete'
```

最终容器：

```bash
docker run -d \
  --name ham-a-exam-trainer \
  --restart unless-stopped \
  -p 18080:18080 \
  -v /home/johnson/sites/ham-a-exam-trainer/www:/srv:ro \
  -v /home/johnson/sites/ham-a-exam-trainer/nginx.conf:/etc/nginx/nginx.conf:ro \
  --label homelab.service=ham-a-exam-trainer \
  --entrypoint nginx \
  docker.1ms.run/jc21/nginx-proxy-manager:latest \
  -g "daemon off;"
```

中间修正：
- 先用本地已有 `busybox:latest` 的 `httpd` 启动过同名容器，但并发 GET 出现 `Empty reply from server`，已替换。
- 探测镜像能力时误启动过临时 Node-RED 容器 `elastic_ramanujan`，已 `docker rm -f elastic_ramanujan` 清理。
- 曾误用 `docker.1panel.live/jc21/nginx-proxy-manager:latest` 前缀触发拉取尝试，已中止；最终使用本机已有 `docker.1ms.run/jc21/nginx-proxy-manager:latest`。

## 验证
容器状态：

```text
ham-a-exam-trainer docker.1ms.run/jc21/nginx-proxy-manager:latest Up ... 0.0.0.0:18080->18080/tcp
```

从 Mac mini 访问 `http://192.168.8.15:18080` 验证：

```text
index     http=200 size=14166  content_type=text/html
app.js    http=200 size=44917  content_type=application/javascript
styles    http=200 size=18810  content_type=text/css
questions http=200 size=598621 content_type=application/javascript
image     http=200 size=10183  content_type=image/jpeg
```

## 回滚
停止并移除该站点容器，站点文件保留：

```bash
docker rm -f ham-a-exam-trainer
```

如需彻底删除 `/home/johnson/sites/ham-a-exam-trainer`，需按 RED-06 单独确认目录范围后再执行。

## 影响
- n100 新增静态 HTTP 服务：`192.168.8.15:18080`。
- `inventory/services.md` 已登记新增服务。
- 未配置 NPM 反代、未配置 DNS、未新增公网端口。

## 后续
- 在 NPM 创建 Proxy Host：`Forward Hostname/IP = 192.168.8.15`，`Forward Port = 18080`，`Scheme = http`。
- 如未来频繁部署静态站点，可把“选择端口 + 同步文件 + 启动静态容器 + 写 log”蒸馏成 `publish-static-site` skill。
