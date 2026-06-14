---
date: 2026-06-14
operator: human+ai
affected: [n100, homelab-ntp]
risk: low
status: success
guardrails: [CONFIRM]
---

# 完成 n100 NTP 迁移：Docker → 系统级 chrony

## 目的
将临时 Docker 版 NTP 服务迁移为 n100 系统级 `chrony.service`，减少对 Docker 的基础时间服务依赖。

## 执行
- 用户在 n100 上安装并启用系统级 `chrony`。
- 用户添加 `/etc/chrony/conf.d/homelab-ntp.conf`：

```text
bindaddress 192.168.8.15
allow 192.168.8.0/24
local stratum 10
```

- AI 验证系统级服务通过后，清理 Docker 版：
  - `docker rm homelab-ntp`
  - `docker image rm homelab/chrony-ntp:20260614`
  - 删除 `/home/johnson/homelab-ntp`

## 验证
- `chrony.service`：`active`
- `systemd-timesyncd.service`：`inactive`
- 监听：`192.168.8.15:123/udp`
- `chronyc tracking`：
  - upstream reference: `time.neu.edu.cn`
  - stratum: `2`
  - system time offset: about `0.4ms`
- NTP 查询 `192.168.8.15:123` 成功：
  - stratum: `2`
  - delta: about `-0.001s`
- Docker 版确认清理：
  - `homelab-ntp` 容器不存在
  - `homelab/chrony-ntp` 镜像不存在
  - `/home/johnson/homelab-ntp` 不存在

## 摄像头后续配置
- NTP server: `192.168.8.15`
- 时区：`GMT+08:00` / `Asia/Shanghai` / `Beijing`
- DST：关闭

## 回滚
如需关闭系统级 NTP 服务：

```bash
sudo systemctl disable --now chrony.service
```

如需移除内网开放配置：

```bash
sudo rm /etc/chrony/conf.d/homelab-ntp.conf
sudo systemctl restart chrony.service
```
