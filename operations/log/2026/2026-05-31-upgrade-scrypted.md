---
date: 2026-05-31
operator: ai
affected: [n100, scrypted]
risk: low
status: success
guardrails: [CONFIRM, PRE-02, PRE-04]
---

# 升级 scrypted 0.137.0 → 0.143.0（项目首个改动类操作）

## 目的
scrypted 落后 6 个小版本（自动更新失效）。用户授权手动升级，不恢复 Watchtower。

## 前置（PRE-02/04）
- 备份卷（容器 root 读取，203M）：`~/scrypted-volume-backup-2026-05-31-1531.tar.gz`（已校验可解）。
- 备份 compose：`~/scrypted-compose.yml.bak-2026-05-31-*`。
- 旧镜像保留可回滚：`1ms.run/koush/scrypted:lite`（2025-02-05, server 0.137.0）。

## 执行
1. `docker compose pull` 失败：配置的镜像源 **`1ms.run` 对该镜像 404（已失效）**。
2. 改 compose `image:` → **`ghcr.io/koush/scrypted:lite`**（官方源；n100 能连 ghcr）。
   - 用 root 容器 `sed` 改 root-owned 文件，避免 sudo。
3. 用户手动把 ghcr 镜像拉到本地后，`docker compose up -d --pull never` 重建。

## 验证
- 容器 `ghcr.io/koush/scrypted:lite`，Up 稳定不重启。
- **server 版本 0.137.0 → 0.143.0**（最新）。
- Web UI `:10443` 返回 302（正常）。最近 30s error 计数 0。

## 已知遗留（非本次回归）
- `OpenVINO Object Detection` 插件加载失败：`No module named pip`。
  原因：**`:lite` 变体不含 Python/ML 依赖**（设计如此），升级前在 lite 上同样无法用。
  → 如需 N100 核显做物体检测，应改用 `:intel` 变体（含 OpenVINO，需透传 `/dev/dri`）。
- ONVIF 某摄像头 `Wrong ONVIF SOAP response` / `Unknown Device unavailable [id:71]`：疑既有摄像头问题，待用户在 UI 核实。

## 回滚
`cd /opt/1panel/docker/compose/scrypted` → 改 image 回 `1ms.run/...`（或用旧 digest sha256:ac43254…）→ `up -d`；必要时解压卷备份覆盖 `scrypted/volume`。

## 影响
- n100：scrypted 容器升级，compose `image:` 改为 ghcr。
- `inventory/services.md`：scrypted 版本/镜像源/lite 限制已更新。

## 后续
- [ ] 用户在 Scrypted UI 确认摄像头/HomeKit/插件正常。
- [ ] 决定是否切 `:intel` 变体启用核显物体检测。
- [ ] 把"docker compose 服务升级"流程蒸馏为 `service-upgrade` skill（本次为首例）。
