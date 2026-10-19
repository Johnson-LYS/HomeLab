---
date: 2026-10-19
type: deployment
affected: [frp-192.168.8.198, ali99-2, frp, nginx, letsencrypt, onepassword]
verified_by: ai
---

# 部署新 FRP 网关与 ali99-2 服务端

## 背景

- 用户已售出原极摩客/PVE，新增一台 Debian 13 软路由设备作为集中 FRP 网关，SSH 别名为 `frp`、地址 `192.168.8.198`。
- 未来应用部署在 n100 (`192.168.8.15`)；由 `frp` 网关转发到 `ali99-2` (`47.109.85.53`)，再由云端 Nginx 通过域名和 HTTPS 暴露。
- 用户明确确认一次性完成软件安装、服务部署、连通验证和文档闭环，并在执行中放行阿里云安全组 `7000/tcp`。

## 变更前状态

- `frp`：Debian 13.7、2 核/7.7 GiB；仅 SSH 监听；没有 zsh、Oh My Zsh、FRP 或 Nginx。
- `ali99-2`：Debian 13.6、2 核/1.7 GiB；已有 Nginx 1.26.3、Certbot 和 `fmo-link.bi8syn.com`，没有 FRP。
- 两台主机均保留原 SSH 入口；未修改家庭路由器、DNS、n100 或现有应用。

## 执行内容

1. 从 FRP 官方 GitHub Release 获取最新 **v0.71.1** Linux amd64 包，核对 SHA-256：`1d9875210972a5d1a62b2dc4c48df45ab0af05d3ca1b5e494a014428259df803`。
2. 在 1Password `HomeLab` vault 新建 `frp-ali99-2-gateway` Password 条目；仓库只记录 `op://HomeLab/frp-ali99-2-gateway/password`，没有输出或提交明文 Token。
3. 在 `ali99-2` 安装 `/usr/local/bin/frps`、独立无登录 `frp` 用户、`/etc/frp/frps.toml` 和加固后的 `frps.service`：
   - 控制端口 `0.0.0.0:7000`；
   - `proxyBindAddr = "127.0.0.1"`；
   - 仅允许代理端口 `18000-18099`；
   - 强制 TLS，使用 `fmo-link.bi8syn.com` 的 Let's Encrypt 证书；
   - Token 从权限为 `0400` 的 `/etc/frp/token` 读取。
4. 新增 Certbot deploy hook `/etc/letsencrypt/renewal-hooks/deploy/20-frps-cert`，续期后把证书复制到 `/etc/frp/tls/`（root:frp、0640）并重启 frps。
5. `ali99-2` 的 Nginx 已存在，因此没有重复安装；本次最终未改变原 `fmo-link.bi8syn.com` 反代行为。
6. 在 `frp` 安装 zsh 5.9、Git、curl、CA 证书和 Oh My Zsh；root 默认 shell 改为 `/usr/bin/zsh`，Oh My Zsh 固定于安装时 commit `964ddf789b022b6958b27d02d7fa54f552de21e9`。
7. 在 `frp` 安装 `/usr/local/bin/frpc`、独立无登录 `frp` 用户、`/etc/frp/frpc.toml`、`/etc/frp/conf.d/` 和加固后的 `frpc.service`：
   - 直接连接 `47.109.85.53:7000`；
   - 校验服务端证书名 `fmo-link.bi8syn.com`；
   - Token 从权限为 `0400` 的 `/etc/frp/token` 读取；
   - 未来每个 n100 应用使用一个独立 TOML 片段。
8. 本机 `~/.ssh/config` 的 `ali99-2` 别名增加 `IdentityFile ~/.ssh/johnson.pub` 与 `IdentitiesOnly yes`，解决 1Password Agent 候选密钥过多导致的认证失败；备份为 `~/.ssh/config.backup-20261019-frp-gateway`。

## 过程中的调整

- 初次发现安全组未放行 7000 后，曾验证通过 Nginx `443/WSS` 接入的替代路径；用户随后开放 7000，因此最终切回标准 TCP + 强制 TLS 方案。
- 临时 WSS Nginx location 已撤销，Nginx 恢复到变更前配置；frps 最终不依赖 Nginx 承载控制通道。
- FRP v0.71.1 不接受尚未进入该发布版 schema 的 `transport.tls.useSystemCa` 字段；严格校验捕获后改为该版本支持的 `trustedCaFile`，再启动服务。

## 验证结果

- `frps verify`、`frpc verify`、`nginx -t` 全部通过。
- `frps.service`、`frpc.service`、`nginx.service` 均为 active；FRP 两端服务均 enabled。
- 两端 FRP 版本均为 **0.71.1**；frpc 日志出现 `login to server success`。
- 从 `frp` 访问 `47.109.85.53:7000` 成功。
- 临时代理 `n100:22` → `ali99-2:127.0.0.1:18000` 建立成功，直连与隧道返回的 ED25519 主机指纹均为 `SHA256:+9OmFACYxWvfPkaOBpsgzea7hfE3CksafEH0u3Gox0I`。
- 验证后临时代理已移出 `/etc/frp/conf.d/`，云端 18000 不再监听；仅保留模板 `/etc/frp/conf.d/n100-app.toml.example`。
- `frps` 的应用代理仅能绑定 `127.0.0.1:18000-18099`，不会直接暴露公网。
- root 的 zsh 5.9 与 Oh My Zsh 非交互加载测试通过。
- 原 `fmo-link.bi8syn.com` Nginx 配置校验通过并保持 active。

## 备份与回滚

- `frp` 备份目录：`/root/homelab-backups/20261019-frp-gateway`。
- `ali99-2` 备份目录：`/root/homelab-backups/20261019-frp-gateway-ali99-2`。
- 回滚 FRP：两端分别执行 `systemctl disable --now frpc` / `systemctl disable --now frps`；恢复备份配置后 `systemctl daemon-reload`。
- 回滚 root shell：在 `frp` 执行 `chsh -s /bin/bash root`，再从备份恢复 `/root/.zshrc`（若原先存在）。
- 回滚 Nginx：恢复 `ali99-2` 备份目录中的 `fmo-link-tls`，执行 `nginx -t && systemctl reload nginx`。

## 后续发布应用

1. 应用部署到 n100，并确认 `frp` 网关可以访问其 IP/端口。
2. 在 `frp:/etc/frp/conf.d/` 增加一个代理片段，将 n100 应用端口映射到未占用的 `18000-18099`。
3. `frpc verify -c /etc/frp/frpc.toml` 后重启 frpc。
4. 在 `ali99-2` 为应用域名增加 Nginx vhost，反代到对应的 `127.0.0.1:18xxx`，签发并自动续期 HTTPS 证书。
5. 完成内网、云端回环和公网 HTTPS 三段验证。
