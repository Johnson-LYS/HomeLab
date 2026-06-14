---
date: 2026-06-14
operator: ai
affected: [n100, go2rtc, 1panel]
risk: low
status: success
guardrails: [CONFIRM, PRE-02, PRE-04]
---

# 部署 go2rtc 摄像头流网关

## 目的
在 n100 的 1Panel compose 目录中部署独立 go2rtc，作为后续 Scrypted / Frigate / Home Assistant 共享摄像头流的基础层。

## 前置
- 用户明确要求部署到 n100，并要求放入 1Panel compose 目录，确保可自动备份打包。
- 已只读确认端口 `1984/8554/8555` 未被占用。
- go2rtc 目录此前不存在；已在 `/opt/1panel/docker/compose/go2rtc/prechange-backup/` 记录部署前 compose 文件清单。
- `johnson` 需要 sudo 密码，未索取密码；通过本机 Docker 权限启动一次性容器写入 root-owned 1Panel compose 目录。

## 执行
在 n100 创建：
```
/opt/1panel/docker/compose/go2rtc/
├── docker-compose.yml
├── 1panel.env
├── data/go2rtc.yaml
├── backup/
└── prechange-backup/
```

`docker-compose.yml`：
- `go2rtc`: `ghcr.io/alexxit/go2rtc:latest`，显式 `platform: linux/amd64`。
- 发布端口：`1984/tcp`、`8554/tcp`、`8555/tcp+udp`。
- 配置目录：`./data:/config`。
- `go2rtc-backup`: `offen/docker-volume-backup:v2.44.0`，每日 `00:00` 打包 `./data` 到 `./backup`，保留 7 天。

初始 `data/go2rtc.yaml` 不含摄像头凭据：
```
streams: {}

webrtc:
  candidates:
    - 192.168.8.15:8555
```

镜像拉取处理：
- n100 直接从 ghcr 拉取较慢，中途终止慢速 `docker compose up -d` 客户端。
- 先从本机 Docker 拉取镜像后 `docker save | ssh n100 docker load`。
- 首次误传 Apple Silicon 本机默认 `linux/arm64` 镜像，n100 上 go2rtc 容器重启；已立即停止并更换为 `linux/amd64` 镜像。
- 最终用 `docker compose up -d --pull never --force-recreate go2rtc` 重建。

## 验证
- `docker image inspect ghcr.io/alexxit/go2rtc:latest`：`linux/amd64`。
- `docker exec go2rtc go2rtc --version`：
  `go2rtc version 1.9.14 (b5948cf) linux/amd64`。
- `docker ps`：`go2rtc` 与 `go2rtc-backup` 均 `Up`。
- `ss -tulpen`：`1984/tcp`、`8554/tcp`、`8555/tcp`、`8555/udp` 均监听。
- `curl http://127.0.0.1:1984/` 返回 `HTTP 200`。
- 手动触发备份：
  `docker exec go2rtc-backup backup`
  生成 `backup-go2rtc-data-2026-06-14T21-53-40.tar.gz`。

## 回滚
```
cd /opt/1panel/docker/compose/go2rtc
docker compose down
```

如需清理文件，由用户确认后再删除 `/opt/1panel/docker/compose/go2rtc`。

## 影响
- n100 新增 go2rtc 服务：
  - Web UI/API: `http://192.168.8.15:1984`
  - RTSP restream: `rtsp://192.168.8.15:8554/<stream>`
  - WebRTC: `192.168.8.15:8555/tcp+udp`
- 新增每日配置备份 tar.gz，保留 7 天。
- `inventory/services.md` 已补充 go2rtc。

## 后续
- [ ] 在 go2rtc Web UI 或 `data/go2rtc.yaml` 中逐步添加摄像头 streams；注意不要把 RTSP 密码写入 git。
- [ ] 决定 Scrypted 是否改为消费 go2rtc 转发流，避免多个系统直接拉摄像头。
