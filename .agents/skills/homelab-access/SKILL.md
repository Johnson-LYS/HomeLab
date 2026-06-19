---
name: homelab-access
description: Use when connecting to or operating any HomeLab device or service — SSH into a server/NAS, reach a service admin UI/API, or look up a host's address, SSH user, port, or which op:// credential to use. Triggers on "ssh/登录/连接到某台设备", running a command on the NUC/QNAP/PVE/Mac mini, or resolving a HomeLab secret from 1Password.
---

# homelab-access

统一的「怎么连 HomeLab 设备 / 服务」入口。两条铁律：
- **SSH 走 1Password Agent**（本地无私钥）。
- **密钥用 `op://` 运行时解析，绝不落盘 / 绝不进文件。**

## 动手前（每次必做）

1. 读 `policies/guardrails.md` —— 本次是否踩红线 / 需人工确认。
2. 读相关 `inventory/` —— 确认目标主机与现状。
3. 改动完成后写 `operations/log/`（黄金法则：同一次提交更新 inventory）。

> 当前阶段 **A + 辅助执行**：只读类可直接做；改动类 AI 出方案、人执行。

## SSH 连接

全局已配置 1Password SSH Agent（`~/.ssh/config` 的 `Host *` → `IdentityAgent .../1password/.../agent.sock`），所有连接复用它，本地不落地私钥。

| 别名 | 设备 | 地址 | 用户 | 端口 | 状态 |
|---|---|---|---|---|---|
| `n100` | 联想百应 NUC · Debian 6.1 | 192.168.8.15 | `johnson` | 22 | ✅ 已连通 |
| `jonas` | QNAP TS-264C | 192.168.8.10 | `Johnson`（大写 J） | 22 | ✅ 已连通（亦 `jonas.jsho.top`） |
| — | 极摩客 · PVE | 192.168.8.16 | ⚠ 待确认（疑 root） | 22 | known_hosts 有，未连 |
| 本机 | Mac mini M4 · 中枢 | 192.168.8.18 / localhost | `liyongsheng` | — | 运维在此本地执行 |

- 用法：`ssh n100 '<命令>'`（如只读 `ssh n100 'docker ps'`）。
- **别用 IP 硬连**已有别名的主机；**别猜用户名**（`jonas` 大写、`n100` 小写，PVE 未知先确认）。

## 服务（HTTP 管理面 / API）

| 服务 | 主机 | 入口 | 凭证 |
|---|---|---|---|
| 1Panel | n100 (.15) | TODO 端口 | `op://HomeLab/1panel/password` |
| PVE | .16 | `https://192.168.8.16:8006` | `op://HomeLab/pve/password` |
| AdGuardHome | n100 (.15) | TODO | `op://HomeLab/adguardhome/password` |
| Nginx Proxy Manager | n100 (.15) | TODO | `op://HomeLab/npm/password` |
| Emby | jonas (.10) | TODO | `op://HomeLab/emby/password` |

完整 / 最新以 `inventory/services.md`、`inventory/credentials.md` 为准（带 TODO 的待 reconcile 补全）。

## 解析密钥（op://）

```bash
op read "op://HomeLab/<item>/<field>"                 # 取单值
op run --env-file=<(echo 'PW=op://HomeLab/npm/password') -- <cmd>   # 注入环境，不落盘
```

前提：`op` 已登录（`op vault list` 可验证）。SSH 私钥不在此——走 Agent。

### Codex 沙箱注意

`op` 依赖 1Password Desktop App integration。Codex 沙箱内可能报：

```text
1Password CLI couldn't connect to the 1Password desktop app
```

这不等于 1Password App 坏了，也不等于 vault 里没有凭据。先用同一条只读命令提升出沙箱做 A/B 对比（例如 `op account list`、`op vault list --format json`、`op item list --vault HomeLab`）。若沙箱外成功，再按 `op://` 运行时解析，禁止打印 secret 值；可以只检查字段 label/type。

已验证案例：`HomeLab` vault 中 `n100` 条目有 `username` / `password` 字段，sudo 时可用 `op://HomeLab/n100/password` 通过 stdin 传给远端命令。

## Common mistakes

- ❌ 密码贴进命令 / 文件 → ✅ 一律 `op://` 运行时解析（会进 git 历史 + AI 上下文）。
- ❌ 直接改动不看护栏 → ✅ 先读 `policies/guardrails.md`。
- ❌ 假设用户名 / 端口 → ✅ 用 ssh config 别名；未知的先确认不猜。
- ❌ 把"ssh config 里有"当成"连得通" → ✅ 首次连通后再把 inventory 标 `verified`。
- ❌ `op` 在沙箱内连不上 Desktop App 就判定凭据缺失 → ✅ 先提升出沙箱复测同一条只读命令。

## 参考

- 主机 / 网络事实：`inventory/devices.md`、`inventory/network.md`
- 凭证引用表：`inventory/credentials.md`
- 安全护栏：`policies/guardrails.md`
