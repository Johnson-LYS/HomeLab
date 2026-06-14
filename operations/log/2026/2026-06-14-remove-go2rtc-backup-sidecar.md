---
date: 2026-06-14
operator: ai
affected: [n100, go2rtc, 1panel]
risk: low
status: success
guardrails: [CONFIRM, PRE-02, PRE-04]
---

# 移除 go2rtc 备份 sidecar

## 目的
用户确认 go2rtc 不需要独立 `offen/docker-volume-backup` sidecar，改为依赖 1Panel 系统快照备份自动打包 compose 目录，减少常驻容器与重复备份。

## 前置
- 当前 go2rtc compose 文件已备份到：
  `/opt/1panel/docker/compose/go2rtc/prechange-backup/docker-compose-before-remove-backup-20260614-144852.yml`
- 保留既有 `backup/` 目录和已生成过的 `backup-go2rtc-data-2026-06-14T21-53-40.tar.gz`，未删除数据文件。

## 执行
修改 `/opt/1panel/docker/compose/go2rtc/docker-compose.yml`：
- 删除 `backup` service。
- 保留 `go2rtc` service、端口、`./data:/config` 配置卷不变。

执行：
```
cd /opt/1panel/docker/compose/go2rtc
docker compose config
docker compose up -d --remove-orphans
```

第一次写入时端口映射出现 `85555:8555/tcp` 笔误，`docker compose config` 失败，未应用；随后重写正确 compose 并成功执行。

## 验证
- `docker compose ps` 仅剩 `go2rtc`，`go2rtc-backup` 已停止并移除。
- `docker ps -a --filter name=go2rtc` 仅显示 `go2rtc`。
- `curl http://127.0.0.1:1984/` 返回 `HTTP 200`。
- `ss -tulpen` 显示 `1984/tcp`、`8554/tcp`、`8555/tcp`、`8555/udp` 仍在监听。

## 回滚
如需恢复独立备份 sidecar：
```
cd /opt/1panel/docker/compose/go2rtc
cp prechange-backup/docker-compose-before-remove-backup-20260614-144852.yml docker-compose.yml
docker compose up -d
```

## 影响
- n100 移除常驻容器 `go2rtc-backup`。
- go2rtc 主服务未重建，持续运行。
- `inventory/services.md` 已更新 go2rtc 备份说明。

## 后续
- [ ] 确认 1Panel 系统快照备份范围确实覆盖 `/opt/1panel/docker/compose/go2rtc`。
