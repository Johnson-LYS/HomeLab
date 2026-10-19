---
date: 2026-08-01
operator: ai
affected: [n100, dashboard-ha]
risk: low
status: success
guardrails: [CONFIRM, PRE-04]
---

# 部署 Dashboard HA（20260801-211049）

## 目的

将本地 `dashboard-ha` 当前工作区版本部署到 n100，作为墙面 iPad 使用的独立 Home Assistant Web/PWA 控制面。

## 部署前检查

- 用户明确要求按 HomeLab 规范部署到 n100，并在 1Password 审核后继续执行。
- n100 架构为 `x86_64`，Docker Server 版本为 `28.3.3`。
- 根分区可用空间约 66 GB。
- 未发现既有 `dashboard-ha` 容器或 Compose 目录。
- 宿主端口 `18081` 未被占用。
- 本次不修改 Home Assistant、Nginx Proxy Manager、AdGuardHome、DNS 或路由器配置。

## 执行

- release：`20260801-211049`
- 本地构建目标：`linux/amd64`
- 镜像：`dashboard-ha:20260801-211049`
- 镜像 ID：`sha256:6204ace16b06175532d3acb097850d5d31d503b3f69fe410c69c127b9f97b732`
- 容器：`dashboard-ha`
- 端口：`18081:8080`
- Compose：`/opt/1panel/docker/compose/dashboard-ha/compose.yaml`
- 重启策略：`unless-stopped`

构建时通过 Docker BuildKit secret 向 Vite 提供前端 HA Token，Token 未写入 Dockerfile、构建参数、Compose 或 HomeLab 仓库。由于该项目按既定设计在浏览器端直连 HA，构建后的前端资源会包含浏览器运行所需的凭证；服务目前仅通过内网端口发布。

镜像经 SSH 流式传输到 n100 后，使用 Docker Compose 首次启动。未停止或重启任何既有容器。

## 验证

容器状态：

```text
dashboard-ha | dashboard-ha:20260801-211049 | 0.0.0.0:18081->8080/tcp | running, healthy
```

HTTP 验证：

```text
http://127.0.0.1:18081/                    200 text/html
http://127.0.0.1:18081/manifest.webmanifest 200 application/octet-stream
http://127.0.0.1:18081/nonexistent-route    200 text/html
http://192.168.8.15:18081/                  200 text/html
```

浏览器只读打开页面后，标题为 `香山府 · 智能中控`。验证过程中未调用任何 HA 写入或设备控制操作。

## 回滚

这是首次部署，没有上一版容器可切换。回滚只需停止并移除本次 Compose 创建的容器和网络，保留镜像及 Compose 文件便于恢复：

```bash
ssh n100 'cd /opt/1panel/docker/compose/dashboard-ha && docker compose down'
```

如需删除镜像或部署目录，必须另行确认具体范围。

## 影响

- n100 新增内网服务 `http://192.168.8.15:18081/`。
- 新增一个 Docker 容器及独立 Compose 网络。
- 未配置公网或域名入口。
- 未影响现有 Home Assistant 及其他容器。
