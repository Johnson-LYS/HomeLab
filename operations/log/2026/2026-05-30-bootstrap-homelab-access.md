---
date: 2026-05-30
operator: ai
affected: [n100, jonas, pve, macmini]
risk: low
status: success
guardrails: [AUTO]
---

# 建立 homelab-access skill（首个地基 skill，纯只读发现）

## 目的
第 1 步起手：把「怎么连 HomeLab 设备」从被验证过的现有配置里整理成 skill，
而非凭空臆想（遵循 AGENTS.md §9「skill 从被验证过的操作里长出来」）。

## 执行
只读发现本机已有的真实访问配置（未连接任何设备）：
- `cat ~/.ssh/config` —— 提取 HomeLab 主机别名与用户。
- `~/.ssh/known_hosts` —— 确认连过的内网主机。
- 确认 1Password SSH Agent 全局启用（`Host *` → `IdentityAgent .../agent.sock`），`agent.sock` 存在。

关键事实（已验证 from ssh config）：
- `n100` = 192.168.8.15 user `johnson` port 22（联想百应 Debian）
- `jonas` = 192.168.8.10 user `Johnson`(大写) port 22（QNAP，亦 jonas.jsho.top）
- `.16`(PVE)、`.18`(Mac mini) 在 known_hosts，无别名

产出：`.agents/skills/homelab-access/SKILL.md`。

## 验证
- 内容全部来自真实 ssh config，无虚构用户名/端口。
- 待确认项（PVE 用户、各服务管理端口）明确标 ⚠/TODO，未编造。
- skill 双工具可发现性：见同批 codex `debug prompt-input` 复核 + Claude 会话 skills 列表。

## 回滚
纯新增文件 + 文档更新，无设备改动。回滚 = `git revert`。

## 影响
- 新增 `.agents/skills/homelab-access/SKILL.md`
- 更新 `inventory/devices.md`（新增「SSH 接入」已验证小节）

## 后续
- [ ] 首次只读连通测试（`ssh n100 true` / `ssh jonas true`）→ 把设备标 `verified`，需用户在场（1Password 授权）。
- [ ] 确认 PVE 的 SSH 用户与各服务管理端口。
- [ ] 下一个地基 skill：`credential-rotation`（需用户配合，涉及 1Password 录入）。
