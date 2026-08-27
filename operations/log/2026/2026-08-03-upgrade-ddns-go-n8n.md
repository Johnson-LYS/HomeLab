---
date: 2026-08-03
operator: ai
affected: [n100, ddns-go, n8n]
risk: medium
status: success
guardrails: [CONFIRM, PRE-04]
---

# 升级 ddns-go 与 n8n

## 目的

升级 n100 上长期未更新的 ddns-go 与 n8n，并固定明确版本，避免继续依赖浮动 `latest`。

## 授权与影响

- 用户确认升级计划后授权 AI 直接执行。
- 两个服务逐个升级，未同时停止。
- ddns-go 与 n8n 各短暂停止并重建一次；未删除旧镜像、数据或备份。

## 升级前状态

- ddns-go：`docker.1panel.live/jeessy/ddns-go:latest`，本地镜像创建于 2025-05-10。
- n8n：`n8nio/n8n:2.15.0`，运行约 3 个月。
- n100 根分区：233G，已用 156G，剩余 65G。
- 两个容器近期日志均未发现 error/fatal/panic。

## 备份

备份目录：`/home/johnson/backups/ddns-n8n-upgrade-20260803-195421`

- `portal-network-compose.yml`
- `n8n-compose.yml`
- `old-image-ids.txt`
- `ddns-go-data.tar.gz`
- `n8n-data.tar.gz`
- 对应 SHA-256 校验文件

全部备份通过 `sha256sum -c` 校验，权限为仅所有者可读写。旧镜像保留用于回滚。

## 执行

1. ddns-go Compose 镜像改为 `jeessy/ddns-go:v6.17.4`。
2. 拉取镜像后停止 ddns-go，备份绑定挂载数据，再重建服务。
3. n8n Compose 镜像从 `2.15.0` 改为 `2.30.5`。
4. n100 直连 Docker Hub 速度过慢，保持旧容器在线并中止远端拉取。
5. 在 Mac mini 明确使用 `--platform linux/amd64` 拉取 n8n 镜像，通过 gzip + SSH 流式导入 n100。
6. 停止 n8n，备份绑定挂载数据，再使用导入镜像重建。

## 验证

- ddns-go：`v6.17.4`，容器运行，重启计数 0，管理端口 `9876` 返回 HTTP 307。
- n8n：`2.30.5`，容器运行，重启计数 0，主页与 `/healthz` 均返回 HTTP 200。
- n8n 数据库迁移全部显示 `Finished migration`。
- n8n 工作流：12 个，其中 6 个启用。
- 两个容器升级后近期日志未发现致命错误。

## 已知提示

- n8n 内置 Python task runner 因镜像不含 Python 3 未启动；日志说明生产环境应使用外部 runner。当前 Web、健康检查及已有工作流数据正常。
- n8n 提示 v3 将调整 binary data 存储目录，并有若干环境变量默认值将在未来变化；本次不扩大范围修改配置。

## 回滚

1. 恢复备份目录中的对应 Compose 文件。
2. 若数据需要回退，在服务停止状态下恢复对应数据归档。
3. 使用保留的旧镜像重建服务。
4. 验证 HTTP、日志与工作流/DNS 状态。

## 后续

- [ ] 观察 24 小时内 ddns-go 更新日志与 n8n 工作流执行情况。
- [ ] 如需在 n8n 使用 Python Code 节点，单独规划外部 task runner。
- [ ] 在升级到 n8n v3 前处理 binary data 路径迁移和默认值变更提示。
