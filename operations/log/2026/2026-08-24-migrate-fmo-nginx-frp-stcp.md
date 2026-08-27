---
date: 2026-08-24
operator: ai
affected: [ali99, pve-vm-107, server-192.168.8.131, nginx, frp, dns, letsencrypt]
risk: high
status: success
guardrails: [CONFIRM, PRE-01, PRE-03, PRE-04]
---

# 将 FMO 静态页迁入宿主机 Nginx并发布 FMO Activity

## 目的与授权

- 用户要求停止 `ali99` 上的 Caddy 静态站点容器，改用宿主机 Nginx，并把站点迁到 `/fmo-companion/`。
- 新域名采用 `fmo-companion.bi8syn.com`；新增 `fmo-activity.bi8syn.com`，经 FRP 转发到 `server` (`192.168.8.131`) 的 `:18088`。
- 用户在查看停机、安装、DNS、证书和 PVE 快照方案后两次明确确认执行；HTTP-01 被阿里云备案策略拦截后，又明确确认安装 acme.sh 改用 TLS-ALPN。

## 前置保护

1. 在 PVE 为 VM 107 (`server`) 创建在线快照 `pre-frp-web-20260824`，满足 PRE-01。
2. 两端保留直连 SSH；原 `ali99:13122` FRP SSH 入口在变更后回归成功，满足 PRE-03。
3. 备份目录为 `ali99:/root/homelab-backups/20260824-1752` 与 `server:/root/homelab-backups/20260824-1752`。
4. 原容器和 `/opt/fmo-companion` 均保留；静态文件复制前后 SHA-256 均为 `1ad323269dbf0513c9477dba0258f8e534dfca06f56b87ef8e016cd1bcb2368e`。

## 执行

1. 在 `server` 的 `/etc/frp/frpc.toml` 增加 `fmo-activity-stcp`，后端为 `192.168.8.131:18088`；复用现有 FRP token 作为 STCP secret，通过 root 管理、`frp` 组只读的本地环境文件注入，未输出或写入仓库。
2. 在 `ali99` 安装同版 FRP **v0.69.0** 客户端，新增 `frpc-visitor.service`，只绑定 `127.0.0.1:18088`；未修改 `frps.allowPorts`，也未新增公网远端端口。
3. 安装 Debian 原生 Nginx **1.22.1**、Certbot；复制静态页到 `/fmo-companion/privacy/index.html`，配置文件为 `/etc/nginx/sites-available/fmo-sites.conf`。
4. 校验 Nginx 配置和两个本地 Host 请求成功后，停止 `fmo-companion-caddy` 并启动 Nginx。旧容器保持 `exited`，未删除容器、卷或原目录。
5. 用户先新增 `fmo-activity.bi8syn.com` A 记录；AI 通过已登录的阿里云控制台新增 `fmo-companion.bi8syn.com` A 记录。两者均指向 `8.138.130.141`，TTL 10 分钟。
6. Certbot HTTP-01 因阿里云返回 `Non-compliance ICP Filing` 403 而失败；未生成 Certbot 证书，随后禁用 `certbot.timer`。
7. 从官方 GitHub Release 固定安装 acme.sh **v3.1.4**；源包 SHA-256 为 `3729439c05ec3671c4584a1c2681640e054b50e2aff0cd04075c2b44e32d1bfa`。
8. acme.sh 通过 Let's Encrypt TLS-ALPN 成功签发 ECC 证书，覆盖 `fmo-companion.bi8syn.com` 与 `fmo-activity.bi8syn.com`；部署路径 `/etc/nginx/ssl/fmo-bi8syn/`。
9. 新增 `acme-fmo-renew.timer` 每日检查续期；保存的 pre/post hook 会在实际续期时短暂停止 Nginx、完成 TLS-ALPN 后重新启动，并通过 reload hook 加载新证书。

## 验证

- Nginx、`frps`、`frpc`、`frpc-visitor` 均为 active + enabled；`acme-fmo-renew.timer` 为 active + enabled。
- `ali99:127.0.0.1:18088` 经 STCP 返回 HTTP 200；`server:18088` 后端返回 HTTP 200。
- 原公网 SSH 通道 `ali99:13122` 回归成功，返回 `host=server user=johnson`。
- Let's Encrypt 证书 SAN 包含两个新域名，有效期为 2026-08-24 至 2026-11-22；ARI 续期时间为 2026-10-23T01:03:06Z。
- Chrome 公网实测隐私政策标题为 `FMO 助手 / FMO Companion 隐私政策`，Activity 标题为 `FMO Activity` 且页面显示真实数据。
- `fmo-companion-caddy` 为 `exited`；没有删除原容器、卷或旧站点目录。

## 回滚

```bash
# ali99：停 Nginx/visitor，恢复旧 Caddy
systemctl stop nginx frpc-visitor
docker start fmo-companion-caddy

# server：恢复备份配置并重启 frpc
cp /root/homelab-backups/20260824-1752/frpc.toml /etc/frp/frpc.toml
cp /root/homelab-backups/20260824-1752/frpc.service /etc/systemd/system/frpc.service
systemctl daemon-reload && systemctl restart frpc

# 如需整机级回滚，可在 PVE 使用 VM 107 快照 pre-frp-web-20260824。
```

DNS 回滚为删除两个新 A 记录或恢复原目标；属于公网入口变更，执行前仍需人工确认。

## 已知限制与风险

- `bi8syn.com` 在阿里云中国大陆入口的 HTTP 请求会被未备案策略拦截，80/tcp 不能可靠完成跳转或 ACME HTTP-01；HTTPS 443 已实测正常。
- TLS-ALPN 续期需要短暂释放 443，因此实际续期时 Nginx 会中断数秒。
- PVE 创建快照时提示 thin pool 逻辑容量超配；当时 `local-lvm` 实际使用率约 17.5%，本次快照成功，但仍应监控 thin pool 容量。
- 公网开放后数秒内即出现自动扫描请求；Activity 后端仅通过 STCP 绑定到 `ali99` 回环地址，未直接暴露 18088。
