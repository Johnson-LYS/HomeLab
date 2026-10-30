---
date: 2026-10-30
type: deployment
affected: [frp, ali99-2, nginx, letsencrypt, n100-ota]
verified_by: ai
source: SSH 配置校验、HTTP/HTTPS 探测、Certbot 签发输出
---

# 发布 OTA 静态文件服务

- 用户授权新增 `ota.bi8syn.com` 映射及证书；DNS 已由用户解析到 `47.109.85.53`。
- 预检：`frp` 可访问 `192.168.8.15:18089`，返回 OTA ready JSON；云端 18089 未占用。n100 容器为 `bi8syn-ota`。
- 两端备份目录均为 `/root/homelab-backups/20261030-ota`，包含变更前客户端片段/Nginx sites。
- 新增 `frp:/etc/frp/conf.d/ota.toml`，代理 `n100-ota`：`192.168.8.15:18089` → `ali99-2:127.0.0.1:18089`。校验配置后重启 frpc，现有隧道短暂重连。
- 新增 `ali99-2:/etc/nginx/sites-available/ota` 及 enabled 软链接；80 保留 ACME webroot，其余请求跳转 HTTPS；443 保留原始 Host，反代回环 18089。关闭代理缓存与缓冲，保留上游缓存和下载语义。
- Certbot webroot 正式签发 ECDSA 证书，SAN 为 `ota.bi8syn.com`，到期 2027-01-28；使用现有 timer 和 `30-nginx-reload` deploy hook。
- `frpc verify` 与 `nginx -t` 通过，云端经隧道读取 ready JSON 成功。
- 公网 HTTPS 首页 200、`Cache-Control: no-store`；健康入口 200；证书名称与有效期校验通过，回环监听实测为 `127.0.0.1:18089`。
- `certbot renew --dry-run --run-deploy-hooks --no-random-sleep-on-renew --cert-name ota.bi8syn.com` 成功，现有 Nginx reload hook 执行通过。
- 回归：Trust `/readyz`、FMO Link `/pki/v1/root.crl.json` 均为 200；Nginx、frps、Certbot timer 均 active。
- 后端文件目录目前为空，因此实际文件的 Range/ETag/断点续传验证需首个发布包上传后执行，本次不创建假 OTA 文件。
- 未修改 n100 容器、文件或家庭路由器；SSH 独立入口保持可用。
- 回滚：移除新增 Nginx enabled 软链接并校验/reload，再将客户端 `ota.toml` 移出 conf.d 并校验/restart；确认回环 18089 停止监听。备份保留可恢复。
