---
date: 2026-06-14
operator: ai
affected: [n100, homelab-ntp]
risk: low
status: in_progress
guardrails: [CONFIRM]
---

# 开始迁移 n100 NTP：Docker → 系统级 chrony

## 目的
用户希望改为系统级 `chrony`，先停止 Docker 版 NTP，释放 UDP/123，随后由用户在 n100 上手工执行 sudo 命令安装系统级服务。

## 执行
- 停止 Docker 容器：`docker stop homelab-ntp`
- 确认容器状态：`Exited (0)`
- 确认 `192.168.8.15:123/udp` 已释放。

## 当前状态
- Docker 版 NTP 已停止但未删除。
- 系统级 `chrony` 尚未安装/验证。
- 等用户执行系统级安装命令后，由 AI 做只读验证；验证通过后删除 Docker 版容器/镜像/构建目录，并追加最终记录。

## 回滚
如系统级安装前需要临时恢复 Docker 版：

```bash
docker start homelab-ntp
```
