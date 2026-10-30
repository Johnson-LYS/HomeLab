---
date: 2026-10-30
type: configuration
affected: [frp, safeline-mgt]
verified_by: ai
---

# 雷池管理入口调整为内网访问

- 用户明确要求不使用 SSH 隧道，管理页面直接在内网访问。
- `/opt/safeline/.env` 的 MGT_PORT 从 `127.0.0.1:9443` 改为 `192.168.8.198:9443`，保留文件 0600 权限。
- 原 env 备份 `/root/homelab-backups/20261030-safeline/env.before-lan-management`（包含凭据，权限 0600）。
- `docker compose up -d --no-deps mgt` 仅重建管理容器，未改 FRP、云端映射及数据入口防护规则。
- 回滚：恢复上述 env 备份，再重建 mgt 容器。
- 实测 Mac 通过 LAN 访问管理首页返回 200；Docker 端口确认为 `192.168.8.198:9443`；Trust readiness 与 OTA healthz 回归均 200。
