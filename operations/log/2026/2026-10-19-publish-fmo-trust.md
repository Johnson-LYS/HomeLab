---
date: 2026-10-19
type: deployment
affected: [n100, frp-192.168.8.198, ali99-2, frp, nginx, letsencrypt, dns]
verified_by: ai
---

# 通过 FRP 与 ali99-2 发布 FMO Trust HTTPS

## 目标与边界

- 将 n100 `192.168.8.15:18090` 上的 FMO Trust 发布为 `https://trust.bi8syn.com` 与 `https://pki.bi8syn.com`。
- 两个域名必须保留原始 Host：`trust` 提供管理 Web/API，`pki` 仅提供 `/fmo/v1/*` 公共路由。
- 不映射独立 PostgreSQL，不创建管理员/Passkey、生产 CA、UID、签名任务或公开产物。
- 用户确认两个 A 记录已创建；阿里云控制台与公共 DNS 均显示它们指向 `47.109.85.53`。

## 变更前检查

- n100 后端按 `trust` Host 返回首页 200、`/readyz` 200；按 `pki` Host 返回根路径 404、未发布公开对象 404。
- `ali99-2:127.0.0.1:18090` 变更前没有监听，位于 frps 已授权的 `18000-18099` 池内。
- `frpc`、`frps`、Nginx 均为 active，FRP 与 Nginx 配置校验通过。
- n100 部署目录及范围以 `/Users/liyongsheng/Projects/fmo-trust/docs/development/n100-deployment.md` 为准。

## 执行内容

1. 在 `frp:/etc/frp/conf.d/fmo-trust.toml` 增加 TCP 代理：
   - `localIP = "192.168.8.15"`
   - `localPort = 18090`
   - `remotePort = 18090`
2. 严格校验 frpc 配置后重启 `frpc.service`；`frps.proxyBindAddr = "127.0.0.1"` 使远端端口仅监听云服务器回环地址。
3. 在 `ali99-2` 创建 `/etc/nginx/sites-available/fmo-trust` 及 enabled 软链接：
   - 80/tcp 保留 ACME webroot 并跳转 HTTPS；
   - 443/tcp 同时服务两个域名；
   - `proxy_pass http://127.0.0.1:18090`；
   - `proxy_set_header Host $http_host` 与 `X-Forwarded-Host $http_host` 保留原始 Host；
   - 最大请求体 6 MiB，与应用单次证据上传边界一致；
   - TLS 仅允许 1.2/1.3，并增加 HSTS、nosniff、no-referrer。
4. Certbot webroot 为两个域名签发同一张 ECDSA Let's Encrypt 证书，SAN 包含两个域名，到期日 2027-01-17。
5. 新增 `/etc/letsencrypt/renewal-hooks/deploy/30-nginx-reload`，证书成功续期后先执行 `nginx -t`，再 reload Nginx。

## 验证

- FRP：`frpc verify` 通过、服务 active；`ali99-2` 仅在 `127.0.0.1:18090` 监听该代理。
- 后端 Host 路由：云端经 FRP 请求 `trust /` 与 `/readyz` 均 200；`pki /` 与未发布公开对象均 404。
- ACME：两个域名的 HTTP challenge 均从公网读取成功；Certbot 正式签发成功。
- HTTPS：固定真实公网 IP 并携带相应 SNI/Host 验证：
  - `trust /` 200；`trust /readyz` 200；
  - `pki /` 404；`pki /readyz` 404；`pki /fmo/v1/__probe__/missing` 404。
- 证书 SAN 同时包含 `trust.bi8syn.com` 与 `pki.bi8syn.com`。
- `certbot renew --dry-run --run-deploy-hooks --cert-name trust.bi8syn.com` 成功，Nginx deploy hook 已执行。
- 原 `fmo-link.bi8syn.com/pki/v1/root.crl.json` 仍返回 200。
- 本机 Surge 使用 Fake-IP `198.18.218.0/24`，因此最终公网直连测试使用 `curl --resolve <域名>:443:47.109.85.53`，同时保留 TLS SNI 和 HTTP Host。

## 备份与回滚

- `frp`：`/root/homelab-backups/20261019-fmo-trust-publication`。
- `ali99-2`：`/root/homelab-backups/20261019-fmo-trust-publication`。
- 回滚顺序：禁用 `fmo-trust` Nginx site 并 reload；移出 `frp:/etc/frp/conf.d/fmo-trust.toml` 并重启 frpc；确认 `127.0.0.1:18090` 停止监听；按需恢复上述备份。
- 证书由 Certbot 管理，不手动修改 `/etc/letsencrypt/live/` 下的链接或私钥。

## 后续

- 管理员本人从 `https://trust.bi8syn.com` 登记首个 Passkey。
- 登记前再次确认浏览器地址栏域名与有效证书；不要使用内网 HTTP Origin 登记。
- 生产 CA、公开链、UID 范围和签名发布仍需单独授权与验收。
