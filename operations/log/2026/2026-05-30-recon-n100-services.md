---
date: 2026-05-30
operator: ai
affected: [n100]
risk: low
status: success
guardrails: [AUTO]
---

# 只读盘点 n100 服务（迷你 reconcile）

## 目的
摸清主力机 n100 上实际跑的服务与端口，填实 `services.md` 的 TODO，
为后续 `publish-service` 等 skill 提供真实依据。

## 执行
只读（未改动）：
```
ssh n100 'docker ps --format ...; ss -tln; df -h /; free -h'
```
发现 30+ docker 服务（1Panel 管理）。详见 `inventory/services.md`。

## 验证
- 硬件实锤与 inventory 一致：内存 7.5Gi(≈8G)、nvme 233G 用 67%(剩 74G)。
- 核心网络服务端口实锤：NPM :80/81/443、AdGuardHome admin :3003、v2fly :13142。

## 关键发现
- **wg-easy / WireGuard（:60085 tcp, :60086 udp）**——之前未知的第三条入内网通道，已记入 `network.md` 远程接入清单。
- 重度自托管：HA/zigbee2mqtt/matter/scrypted（智能家居）、immich（相册）、n8n/qinglong（自动化）、grafana+prometheus（监控，AI 运维可复用）、new-api（AI 网关）、teslamate、freshrss、nocodb、bark 等。
- bark-server（:8787）可作为未来告警推送出口。

## 回滚
纯只读，无需回滚。

## 影响
- `inventory/services.md`：联想百应段重写为真实服务目录（分类 + 端口）。
- `inventory/network.md`：新增「已知远程接入通道」（3 条入内网路径）。

## 后续
- [ ] 确认 immich 数据卷位置 / 是否落在 QNAP。
- [ ] 1Panel 本体管理端口（未在 docker 列表体现）。
- [ ] 各服务后台凭证 → `credential-rotation` 时逐一入 1Password。
- [ ] PVE (.16) 同样只读盘点。
