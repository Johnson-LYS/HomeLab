---
date: 2026-08-12
operator: ai
affected: [ali99, n100, teslamate-ali99]
risk: high
status: success
guardrails: [CONFIRM, PRE-04]
---

# 将 ali99 TeslaMate 独立迁移到 n100

## 目的与授权

- 用户明确要求停止 `ali99` 上的 TeslaMate 并迁移到 `n100`。
- 只读盘点发现 n100 已有一套 TeslaMate 4.0.1；用户进一步确认迁入实例必须单独运行、互不影响。
- 回滚命令在停机前确认；源端容器、Compose、数据卷均保留，不做删除。

## 源端盘点

- SSH：`ali99`（Debian 6.1，Docker 28.4）。
- 应用项目：`/root/teslamate/kjh/docker-compose.yaml`，包括 TeslaMate 2.1.1、Grafana、TeslaMateAPI、Mosquitto。
- 数据库项目：`/root/database/docker-compose.yaml`，PostgreSQL 17.6，数据库仅有 `postgres` 与 `teslamate_kjh`。
- 迁移前数据：1 台车辆、941 次行程；行程范围 `2025-09-05 08:04:54.528` 至 `2026-08-10 01:04:47.402`。

## 执行

1. 在 n100 预置 `/home/johnson/teslamate-ali99`，环境文件权限设为 `0600`；未向仓库或命令输出写入密码、token、加密密钥。
2. 按源容器实际 image ID 固定并核对五个镜像，避免 `latest` 漂移；迁入实例使用专用镜像标签，不改变其它容器的重建版本。
3. 停止 ali99 的 TeslaMate、Grafana、TeslaMateAPI、Mosquitto，保留 PostgreSQL 在线导出。
4. 创建 PostgreSQL custom-format dump，并分别归档 Grafana、Mosquitto、import 数据；源备份目录：`/root/teslamate-migration-20260812-ali99-to-n100`。
5. 所有归档经 `SHA256SUMS` 校验后复制到 n100；目标副本位于 `/home/johnson/teslamate-ali99/migration`。
6. 在 n100 创建独立 Compose 项目 `teslamate-ali99`、独立网络与四个独立数据卷，恢复数据库和应用数据。
7. 发布端口：TeslaMate `4001`、Grafana `3005`、TeslaMateAPI `8083`、Mosquitto `1884`；PostgreSQL 不发布宿主端口。
8. 目标验证成功后停止 ali99 的 PostgreSQL；源端五个容器均为 exited，原卷保留。

## 验证

- 新实例五个容器连续观测 restart count 为 0。
- HTTP：TeslaMate `:4001` 返回 200；Grafana `:3005` 返回 302；TeslaMateAPI `:8083` 返回 200。
- MQTT 日志确认 TeslaMate 与 TeslaMateAPI 均连接到迁入栈的独立 Mosquitto。
- 目标数据库复核仍为 1 台车辆、941 次行程，行程时间范围与源端一致。
- n100 原有实例 `:4000/:3004/:8082` 同期返回 200/302/200，共享 PostgreSQL 18 未改动。
- n100 根分区迁移后使用率 74%，可用约 59 GiB；可用内存约 2.0 GiB。

## 已知事项

- 新实例访问 Nominatim 反向地理编码时偶发 5 秒超时；不影响 Tesla API、MQTT、HTTP 或数据库运行。
- TeslaMateAPI 沿用源端行为：缺少可选 `allow_list.json` 时记录错误并忽略，但 API 可正常返回 200。

## 回滚

1. 在 n100 执行 `cd /home/johnson/teslamate-ali99 && docker compose stop`，避免两套实例同时轮询同一车辆。
2. 在 ali99 执行 `cd /root/database && docker compose start`，等待 PostgreSQL ready。
3. 在 ali99 执行 `cd /root/teslamate/kjh && docker compose start`。
4. 验证 ali99 原端口和数据库计数；如需再次迁移，使用两端已校验备份。

## 影响

- 更新 `inventory/devices.md`：登记并核实 `ali99` SSH 主机及停机状态。
- 更新 `inventory/services.md`：登记 n100 上独立的 `teslamate-ali99` 栈、端口、路径与数据库边界。
- 新增本操作记录；未修改 n100 原 TeslaMate、共享 PostgreSQL、NPM、AdGuardHome 或网络配置。
