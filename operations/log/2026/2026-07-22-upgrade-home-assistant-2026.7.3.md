---
date: 2026-07-22
operator: ai
affected: [n100, homeassistant, database-postgres, docker-registry]
risk: medium
status: success-with-followups
guardrails: [CONFIRM, PRE-04]
---

# Home Assistant 2026.3.1 → 2026.7.3

## 目的与授权

- 用户明确要求升级 Home Assistant，并同意配置 1ms Docker 镜像加速认证。
- Home Assistant 在备份与升级期间短暂停机；共享 PostgreSQL 和其他服务未停止。

## 升级前检查

- 原版本：Core `2026.3.1`，镜像 `homeassistant/home-assistant:2026.3`。
- 部署目录：`/opt/1panel/docker/compose/homeassistant`；host network；配置 bind mount 到 `config/`。
- 根分区升级前可用约 55 GB。
- 配置检查发现既有和风天气 YAML 不符合当前 custom integration schema；未因本次升级修改。
- 未扫描到 2026.7 已失效的 purpose-specific automation trigger/condition 键名。

## 1ms 镜像加速

- n100 的 Docker daemon 已存在 `https://docker.1ms.run/` registry mirror，无需修改 `daemon.json` 或重启 Docker daemon。
- 按 1ms 官方规则使用固定 Registry 用户名完成付费认证；密钥仅通过交互 stdin 输入，未写入仓库或日志。
- 使用 `docker.1ms.run/homeassistant/home-assistant:2026.7.3` 成功拉取，digest：`sha256:6937c6c51d2f5d6aa66d97e4a68f845bcccd5f9b62cd91992bd6d79b20fe2b3c`。
- Docker 将 registry auth 以可逆形式写入 `/home/johnson/.docker/config.json`；需迁移到符合密钥策略的 credential helper / 1Password 运行时方案。

## 备份与升级

- 备份目录：`/home/johnson/backups/homeassistant-2026.7.3-20260722`。
- 内容：升级前 Compose、完整 `config.tar.gz`（约 62 MB）、PostgreSQL 18 custom-format dump（约 1.6 GB）、`SHA256SUMS`。
- `pg_restore --list` 与 SHA-256 校验通过。
- Compose 镜像固定为 `docker.1ms.run/homeassistant/home-assistant:2026.7.3`，重建并启动容器。

## 验证

- Core：`2026.7.3`。
- HTTP `127.0.0.1:8123`：200。
- 容器：running，restart count 0，未 OOM；验证时约 792 MiB 内存。
- Recorder：Home Assistant 数据库存在 2 个活动连接，`states` 最新时间持续推进。
- 未观察到 MQTT broker、Matter server 或 Recorder 数据库连接失败。

## 已知问题 / 后续

- [ ] 和风天气 custom integration：旧 YAML 使用 `location`，缺少 `latitude` / `longitude`，sensor/weather setup 失败；升级前检查已存在。诊断输出意外显示 API key，应轮换该 key。
- [ ] 海尔 custom integration：refresh token 返回授权失败，需在 HA 中重新认证。
- [ ] Node-RED 发布的地暖 MQTT discovery payload 不符合新版严格 schema：`temperature_unit` 应使用 `C`/`F`，另有 binary sensor / switch topic 缺少对应必需字段。
- [ ] 一个 HomeKit Bridge 引用了不可用的 `switch.xiao_mi_cha_zuo_ups`，启动失败；确认实体恢复后重载或修正桥接配置。
- [ ] 若干模板对 `unavailable` 直接使用 `| float` 且未给 default，启动时产生 TemplateError。
- [ ] 用户在对话中提供了 1ms 密钥；配置完成后应在 1ms 后台轮换，并将新密钥存入 1Password。

## 回滚

1. 停止 Home Assistant。
2. 恢复备份目录中的 `docker-compose.yml.pre-upgrade`。
3. 如配置存储迁移导致不兼容，以 root 权限恢复 `config.tar.gz`。
4. 如 Recorder 数据需要回退，使用已校验的 PostgreSQL custom-format dump 恢复 `homeassistant` 数据库。
5. 启动原 `2026.3` 容器并验证 HTTP、日志与数据库连接。
