---
date: 2026-08-02
operator: ai
affected: [n100, dashboard-ha]
risk: low
status: success
guardrails: [CONFIRM, PRE-04]
---

# 修复 Dashboard HA 私网 HTTP 配置（20260802-175138）

## 现象

首次部署后，浏览器启动阶段抛出 Zod 配置错误：live 模式使用私网 HTTP 地址，但构建镜像未显式启用允许私有网络 HTTP 的安全开关。

## 原因

Dockerfile 已传递 `VITE_HA_MODE` 与 `VITE_HA_URL`，但遗漏 `VITE_HA_ALLOW_INSECURE_PRIVATE`。因此 `http://192.168.8.15:8123` 在前端环境校验阶段被拒绝。HA Token 和 Home Assistant 服务本身无异常。

## 执行

- 在 dashboard-ha Dockerfile 增加 `VITE_HA_ALLOW_INSECURE_PRIVATE` 的 `ARG` 和 `ENV`。
- 使用 `VITE_HA_ALLOW_INSECURE_PRIVATE=true` 构建 `linux/amd64` 修复镜像。
- 新 release：`20260802-175138`。
- 新镜像：`dashboard-ha:20260802-175138`。
- 新镜像 ID：`sha256:9fde46e1d5d865e9c18205c409e5c93ce0360261b1ea64a10fcaf1561b409527`。
- 切换前备份 Compose 为 `/opt/1panel/docker/compose/dashboard-ha/compose.yaml.backup-20260802-175138`。
- 使用 Docker Compose 重建 `dashboard-ha` 容器，端口仍为 `18081:8080`。
- 旧镜像 `dashboard-ha:20260801-211049` 保留用于回滚。

该开关仅允许项目校验认可的 RFC1918 私网地址或 localhost 使用 HTTP，不放宽公网 HTTP 限制。HA Token 仍通过 BuildKit secret 提供，未写入 Dockerfile、Compose 或 HomeLab 仓库。

## 验证

- HA 环境配置测试：7/7 通过。
- 本地修复容器：running、healthy，HTTP 200。
- 本地浏览器：页面完整渲染，显示 `HA 已连接`，控制台无错误。
- n100 容器：running、healthy，HTTP 200。
- 局域网浏览器实际加载 `/assets/index-2ol43DT0.js`。
- 部署页面从 `正在连接` 进入 `HA 已连接`，天气及实体状态正常读取。
- 验证过程未调用任何 HA 写入或设备控制操作。

## 回滚

恢复备份 Compose 后重建容器：

```bash
ssh n100 '
  cd /opt/1panel/docker/compose/dashboard-ha
  sudo cp compose.yaml.backup-20260802-175138 compose.yaml
  docker compose up -d
'
```

回滚目标镜像为 `dashboard-ha:20260801-211049`。本次未删除旧镜像或备份文件。

## 影响

- 修复 Dashboard HA 在私网 HTTP HA 地址下的启动错误。
- `dashboard-ha` 容器因镜像切换被重建一次。
- 未修改 Home Assistant、NPM、DNS、路由器或其他容器。
