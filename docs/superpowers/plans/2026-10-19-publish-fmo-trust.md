# FMO Trust 公网发布实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 n100 的 FMO Trust HTTP 入口通过 FRP 和 ali99-2 Nginx 安全发布为 `trust.bi8syn.com` 与 `pki.bi8syn.com` HTTPS 服务。

**Architecture:** `frp` 客户端把 `192.168.8.15:18090` 映射到 `ali99-2:127.0.0.1:18090`；ali99-2 Nginx 为两个域名终止 TLS，并将原始 Host 转发给后端。应用代理端口不对公网开放。

**Tech Stack:** FRP v0.71.1、Nginx 1.26.3、Certbot/Let's Encrypt、systemd。

**Spec:** `/Users/liyongsheng/Projects/fmo-trust/docs/development/n100-deployment.md`

## Global Constraints

- 两个域名必须保留原始 Host。
- 不转发 PostgreSQL 或其他容器端口。
- 不创建管理员、Passkey、生产 CA、UID 或签名任务。
- 变更前备份；配置校验成功后才能 reload/restart。
- FRP 远端端口仅绑定 ali99-2 回环地址。

## Review Focus

- `trust` 首页及 `/readyz` 必须返回 200。
- `pki` 根路径和未发布公开证书保持 404，不能暴露管理页面。
- 两个证书域名必须匹配并能自动续期。
- Nginx 向后端传递 `$http_host`，不得把 Host 改成回环地址。
- 既有 `fmo-link` Nginx 服务和 n100 既有容器必须保持运行。

---

### Task 1: FRP 映射

**Files:**
- Create: `frp:/etc/frp/conf.d/fmo-trust.toml`

- [x] 备份客户端配置并确认远端端口 18090 未占用。
- [x] 创建 `192.168.8.15:18090` → `ali99-2:127.0.0.1:18090` TCP 代理。
- [x] 执行 `frpc verify`，重启客户端并从 ali99-2 验证两个 Host 的预期响应。

### Task 2: Nginx 与 HTTPS

**Files:**
- Create: `ali99-2:/etc/nginx/sites-available/fmo-trust`
- Create: `ali99-2:/etc/nginx/sites-enabled/fmo-trust`
- Create: `ali99-2:/etc/letsencrypt/live/trust.bi8syn.com/*`（Certbot 管理）

- [x] 确认两个 A 记录均解析到 `47.109.85.53`。
- [x] 备份 Nginx 配置，先安装 ACME HTTP challenge vhost 并执行 `nginx -t`。
- [x] 为两个域名签发同一张 ECDSA 证书。
- [x] 安装 HTTPS vhost，保留 Host 并反代 `127.0.0.1:18090`。
- [x] 验证公网首页、readiness、公开路由隔离、证书 SAN、续期配置和既有站点。

### Task 3: 文档闭环

**Files:**
- Modify: `inventory/network.md`
- Modify: `inventory/services.md`
- Create: `operations/log/2026/2026-10-19-publish-fmo-trust.md`

- [x] 登记公网域名、FRP 映射、证书和验证结果。
- [x] 执行敏感信息扫描与 `git diff --check`。
- [x] 提交前完成最终配置与文档复核。
