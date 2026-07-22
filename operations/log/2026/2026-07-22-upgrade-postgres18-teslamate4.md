---
date: 2026-07-22
operator: ai
affected: [n100, database-postgres, homeassistant, nocodb, teslamate]
risk: high
status: success
guardrails: [CONFIRM, PRE-04]
---

# 升级共享 PostgreSQL 17.6 → 18.4 与 TeslaMate 3.0.0 → 4.0.1

## 目的

升级 n100 上的 TeslaMate。因 TeslaMate 4 要求 PostgreSQL 18，先安全迁移承载 Home Assistant、NocoDB、TeslaMate 的共享 PostgreSQL，再升级 TeslaMate 栈。

## 授权与影响

- 用户修改 `policies/guardrails.md`，允许在主动明确授权下由 AI 执行改动。
- 用户明确允许暂停所有相关服务，并在正式停机切换前再次确认。
- 停止写入方：`homeassistant`、`nocodb-noco-1`、TeslaMate/Grafana/API。
- 未删除任何数据库卷、备份或旧配置。

## 前置检查与演练

- 源数据库：PostgreSQL 17.6；数据库：`homeassistant`、`nocodb`、`teslamate`、`postgres`。
- TeslaMate 数据库扩展：`cube 1.5`、`earthdistance 1.2`、`plpgsql 1.0`。
- 在线预备份：`/home/johnson/backups/postgres-17-to-18-20260722-171524`，全部 archive/checksum 校验通过。
- 使用隔离容器 `pg18-migration-test-20260722` 和独立卷 `database_postgres18_test_20260722` 完成 PostgreSQL 18.4 全库恢复演练。
- 演练中表数、索引数和扩展与 PG17 一致；旧生产服务未受影响。

## 正式迁移

1. 停止所有写入方，确认共享数据库业务连接数为 0。
2. 创建停写后的最终备份：
   - `/home/johnson/backups/postgres-17-to-18-final-20260722-175325`
   - `globals.sql` 与四个数据库 custom-format dump 均通过 `pg_restore --list` 和 SHA-256 校验。
3. 备份数据库 compose：
   - `/opt/1panel/docker/compose/database/docker-compose.yml.pre-pg18-20260722-175325`
4. 数据库 compose 修改：
   - `docker.1ms.run/postgres:17` → `postgres:18.4-trixie`
   - `postgres-data:/var/lib/postgresql/data` → `postgres18-data:/var/lib/postgresql`
5. 创建生产卷 `database_postgres18-data`，启动 PostgreSQL 18.4，恢复角色和全部数据库。
6. 保留旧卷 `database_postgres-data`，未修改、未删除。
7. 启动原应用版本验证 PG18：Home Assistant、NocoDB、TeslaMate 均成功连接并通过 HTTP/数据读取检查。

## TeslaMate 升级

- compose 备份：`/opt/1panel/docker/compose/teslamate/docker-compose.yml.pre-v4-20260722-175325`
- 镜像固定版本：
  - `teslamate/teslamate:4.0.1`
  - `teslamate/grafana:4.0.1`
  - `tobiasehlert/teslamateapi:1.25.0`
- n100 直拉镜像过慢，改由 Mac mini 拉取 `linux/amd64` 镜像，经 gzip + SSH 流式导入。

## 验证

- PostgreSQL：18.4，`pg_isready` 成功。
- HTTP：TeslaMate 200、Grafana 200、TeslaMateAPI 200、Home Assistant 200、NocoDB 302（登录跳转）。
- 数据抽查：TeslaMate 1 台车辆、2434 次行程；Home Assistant `states` 约 4219 万行。
- 数据库连接：Home Assistant、NocoDB、TeslaMate 均成功连接 PG18。
- TeslaMate v4 日志：数据库修复任务均为 `OK`，页面请求返回 200。
- Grafana 无升级后 error 日志。
- TeslaMateAPI 报可选 `allow_list.json` 不存在并忽略；API 仍返回 200。
- 升级后 TeslaMate 备份：`/home/johnson/backups/teslamate-v4-postupgrade-20260722-182509`，archive/checksum 校验通过。

## 回滚

数据库回滚：停止写入方，恢复 `docker-compose.yml.pre-pg18-20260722-175325`，重新启动原 PostgreSQL 17 配置与保留的 `database_postgres-data` 卷，再启动依赖服务。

TeslaMate 回滚：恢复 `docker-compose.yml.pre-v4-20260722-175325` 并重建栈；如数据库 schema 已由 v4 修改，则使用停写前最终备份恢复对应数据库。

## 遗留

- [ ] 观察 24 小时后再决定是否清理隔离演练容器/卷和旧 PG17 卷；当前全部保留。
- [ ] 检查共享数据库 backup sidecar 的 SQL dump hook；迁移前 `/dump` 中未发现现成 dump。
- [ ] 配置 TeslaMateAPI `allow_list.json`，或确认当前忽略白名单符合预期。
- [ ] 轮换本次诊断中意外进入工具输出的数据库密码与 TeslaMateAPI token。
