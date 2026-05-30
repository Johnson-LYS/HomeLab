---
date: 2026-05-30
operator: ai
affected: [n100, jonas]
risk: low
status: success
guardrails: [AUTO]
---

# 只读 SSH 连通验证（首次真实接触设备）

## 目的
把 `homelab-access` 中 `n100`/`jonas` 从「ssh config 里有」证实为「连得通」，
flip inventory 状态为 verified。这是项目第一次真实接触设备（仍为只读）。

## 执行
经 1Password SSH Agent，只读探测（未做任何改动）：
```
ssh -o ConnectTimeout=10 n100  'hostname; whoami; uname -sr'
ssh -o ConnectTimeout=10 jonas 'hostname; whoami; uname -sr'
```

结果（exit=0）：
- n100 (192.168.8.15): host=`debian-mini` user=`johnson` os=`Linux 6.1.0-37-amd64`（Debian）
- jonas (192.168.8.10): host=`Jonas` user=`Johnson` os=`Linux 5.10.60-qnap`（QNAP QTS）

## 验证
两台 exit=0，返回真实主机名/OS，确认 1Password Agent 转发链路可用。

## 回滚
纯只读，无需回滚。

## 影响
- `inventory/devices.md`：SSH 接入表加主机名/OS/状态，n100 & jonas 标 ✅ 已连通。
- `.agents/skills/homelab-access/SKILL.md`：状态列改为 ✅ 已连通。

## 后续
- [ ] PVE (.16) 的 SSH 用户与连通性（疑 root，待确认）。
- [ ] 各服务管理端口（1Panel/AdGuardHome/NPM/Emby）。
- [ ] 下一地基任务 `credential-rotation`（需用户配合 1Password 录入）。
- 发现：n100 真实 hostname `debian-mini`，与另一台 192.168.6.252 同名，注意区分。
