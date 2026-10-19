---
date: 2026-08-27
operator: ai
affected: [ali99, nginx, app-bi8syn-com]
risk: medium
status: success
guardrails: [CONFIRM, PRE-02, PRE-04]
---

# 部署 SSTV+ 隐私政策与支持页到 app.bi8syn.com/sstv-plus/

## 原因与授权

- SSTV+ 上架 App Store 需要 Privacy Policy URL 与 Support URL 两个公开地址。
- 用户明确要求按 `docs/runbooks/deploy-static-privacy-page.md` 部署到 `/sstv-plus/`。
- 站点由 Hugo 构建，产物为 5 个自包含 HTML，零 JavaScript、零外部资源、CSS 全内联，与本站严格 CSP（`default-src 'none'; style-src 'unsafe-inline'`）天然兼容。

## 与 runbook 的偏离

runbook 预设「一个 app 一个单文件隐私页」，路径 `/<app-slug>/privacy/index.html`。本次交付是**中英双语 × 隐私政策/支持页 + 根跳转页 = 5 个文件**，页面之间以相对链接互连。

若照单文件模式部署，中文页上的语言切换器与页脚链接会全部成为死链，且英文版与支持页无法上线，而 Support URL 是 App Store Connect 的必填项。经用户确认，改为**沿用 runbook 的精确匹配 location 模式，为每个文件各写一段**，从而保留 runbook 的安全属性（不使用前缀匹配、`location / { return 404; }` 兜底不变），代价是 URL 形状偏离 `/<app-slug>/privacy/` 惯例。

## 执行

1. 只读检查：Nginx 1.22.1 active+enabled、`nginx -t` 通过、`acme-fmo-renew.timer` active、`/sstv-plus` 不存在（首次部署）。
2. 备份 Nginx 配置到 `ali99:/root/homelab-backups/20260827-234445/fmo-sites.conf`。
3. 上传产物到 `/tmp/sstv-plus-stage/`，以 `install` + `mv` 原子方式部署到 `/sstv-plus/`，目录 0755、文件 0644、root:root，随后清理暂存目录。
4. 在 `/etc/nginx/sites-available/fmo-sites.conf` 的 `app.bi8syn.com` HTTPS server 块内、兜底 `location /` 之前，新增 7 段精确匹配 location：`/sstv-plus` 308 到带尾斜杠地址，`/sstv-plus/` 与 5 个文件各一段，均使用 `root /;` + `default_type text/html;`。
5. `nginx -t` 通过后 `systemctl reload nginx`。

## 验证

- 服务器经公网 IP 的完整 TLS 路径：`/sstv-plus` 返回 308 指向 `/sstv-plus/`；`/sstv-plus/`、`/sstv-plus/index.html`、`zh-hans/privacy.html`、`zh-hans/support.html`、`en/privacy.html`、`en/support.html` 全部 200、`Content-Type: text/html`。
- 安全响应头齐全：CSP、`Referrer-Policy: no-referrer`、`X-Content-Type-Options: nosniff`、`X-Frame-Options: DENY`。
- 兜底与越权探测均为 404：`/sstv-plus/nonexistent.html`、`/sstv-plus/zh-hans/`（无目录列表）、`/etc/passwd`、`/root/`。
- 证书 SAN 覆盖 `app.bi8syn.com`，有效期 2026-08-27 至 2026-11-25。

### 两处过程记录

- reload 后立即发起的前三个请求返回 404，随后请求全部正常。为平滑重载期间旧 worker 仍使用旧配置所致，非配置缺陷；稍后重测全部通过。**结论：reload 后应稍候再验证，否则会误判。**
- 从操作者的 Mac 无法经公网访问，`app.bi8syn.com` 被解析为 `198.18.73.214`（Surge fake-IP 段），TLS 握手报 `SSL_ERROR_SYSCALL`。以**早已上线的 `/fmo-companion/privacy/` 作对照，从同一台机器访问报完全相同的错误**，据此判定为本机既有网络路径问题，与本次部署无关。按 RED-02 未触碰 Surge 网关。

## 公开地址

| 用途 | URL |
|---|---|
| 入口（308 到中文隐私政策） | `https://app.bi8syn.com/sstv-plus/` |
| Privacy Policy URL | `https://app.bi8syn.com/sstv-plus/zh-hans/privacy.html` |
| Support URL | `https://app.bi8syn.com/sstv-plus/zh-hans/support.html` |
| 英文隐私政策 | `https://app.bi8syn.com/sstv-plus/en/privacy.html` |
| 英文支持页 | `https://app.bi8syn.com/sstv-plus/en/support.html` |

## 回滚

恢复 Nginx 配置，使 `/sstv-plus/*` 重新落入兜底 404：

```bash
install -o root -g root -m 0644 \
  /root/homelab-backups/20260827-234445/fmo-sites.conf \
  /etc/nginx/sites-available/fmo-sites.conf
nginx -t && systemctl reload nginx
```

本次为首次部署，无旧页面备份。页面文件可暂时保留在 `/sstv-plus/`，确认无需保留后再清理：

```bash
rm -rf /sstv-plus
```
