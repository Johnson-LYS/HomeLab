---
date: 2026-08-27
operator: ai
affected: [ali99, nginx, letsencrypt, app-bi8syn-com]
risk: high
status: success
guardrails: [CONFIRM, PRE-03, PRE-04]
---

# 将 FMO 隐私政策统一到 app.bi8syn.com 路径

## 原因与授权

- 用户访问 `https://app.bi8syn.com/fmo-companion/privacy` 时失败。
- 只读诊断确认 `app.bi8syn.com` 已指向 `ali99`，但当时证书不含该域名，Nginx 也没有 `/fmo-companion/privacy` 路由；忽略证书错误后的实际响应为 404。
- 用户明确确认扩展证书和修改 Nginx 路由。

## 执行

1. 将现有 Nginx、SSL snippet 和 ACME domain 配置备份到 `ali99:/root/homelab-backups/20260827-app-domain`。
2. `ali99` 当时直连 `acme-v02.api.letsencrypt.org:443` 发生 TLS 超时；建立一次性 SSH reverse dynamic SOCKS 通道 `ali99:127.0.0.1:11080`，仅代理本次 ACME API 出站，请求完成后立即关闭，未写入持久配置。
3. acme.sh 使用 TLS-ALPN 扩展原 ECC 证书，SAN 增加 `app.bi8syn.com`；证书仍覆盖 `fmo-companion.bi8syn.com` 和 `fmo-activity.bi8syn.com`。
4. 更新 `/etc/nginx/sites-available/fmo-sites.conf`：
   - 新增 `app.bi8syn.com/fmo-companion/privacy` → 308 到带尾斜杠的规范地址；
   - `app.bi8syn.com/fmo-companion/privacy/` 直接提供 `/fmo-companion/privacy/index.html`；
   - 原 `fmo-companion.bi8syn.com/privacy/` 308 跳转到统一地址；
   - `fmo-activity.bi8syn.com` 的 FRP 反代保持不变。
5. 首次使用文件级 `alias` 的精确目录 location 触发 index 内部重定向并返回 500；未对公网宣布完成。随后改为 `root /` 文件映射，再次 `nginx -t`、reload 和端到端验证成功。

## 验证

- `https://app.bi8syn.com/fmo-companion/privacy/` 公网返回 HTTP 200、内容长度 13679，并带原有 CSP、Referrer-Policy、nosniff、DENY 安全头。
- `https://fmo-companion.bi8syn.com/privacy/` 公网返回 308，目标为统一地址。
- `fmo-activity.bi8syn.com` 本机 HTTPS 回归为 200；FRP 配置与服务未修改。
- 新证书有效期为 2026-08-27 至 2026-11-25，SAN 包含三个域名；下次 ARI 续期时间为 2026-10-26T00:00:22Z。
- Nginx、`frps`、`frpc-visitor`、`acme-fmo-renew.timer` 均为 active + enabled；临时 11080 监听已关闭。

## 回滚

```bash
cp /root/homelab-backups/20260827-app-domain/fmo-sites.conf /etc/nginx/sites-available/fmo-sites.conf
nginx -t && systemctl reload nginx
```

- 备份还包含修改前的 SSL snippet 和 ACME domain 配置；证书增加 SAN 不影响旧域名，可不回滚证书。
- 任何 DNS 回滚仍需单独人工确认，本次未修改 DNS。

## 已知风险

- `ali99` 本次直连 Let's Encrypt API 曾持续超时；续期 timer 每日重试，若接近 2026-10-26 仍无法直连，应提前建立稳定的受控出站代理或改用可自动化的 DNS-01。
- 阿里云未备案 HTTP 拦截仍存在，用户应直接使用 HTTPS 地址。
