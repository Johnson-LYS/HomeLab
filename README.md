# HomeLab

家庭服务器 / NAS / 网络设备的 **AI 运维**项目。仓库即「运维大脑」，由 Claude Code 与 Codex 共同驱动。

## 这是什么

把家里设备的运维从手动迁移到 AI 运维。仓库承载四类知识：

- **有什么** → [`inventory/`](inventory/)：设备、网络、服务、凭证引用（事实）
- **怎么做** → [`.agents/skills/`](.agents/skills/)：可复用能力（双工具共享）
- **发生过什么** → [`operations/`](operations/)：操作记录 + 故障复盘（历史）
- **不能碰什么** → [`policies/guardrails.md`](policies/guardrails.md)：安全边界

目标是**自主运维（C）**，当前处于 **A + 辅助执行**阶段。

## 给 AI 的入口

- **总纲（必读）**：[`AGENTS.md`](AGENTS.md) —— 唯一真相源，Codex 直接读，Claude 经 `CLAUDE.md` 导入。
- 设计与决策记录：[`docs/plans/`](docs/plans/)

## 给人的入口

- 想了解整体设计与为什么这么做 → [`docs/plans/2026-05-30-homelab-ai-ops-design.md`](docs/plans/2026-05-30-homelab-ai-ops-design.md)
- 想知道当前环境长什么样 → [`inventory/`](inventory/)

## 双工具机制（一句话）

skill 真身只在 `.agents/skills/`：Codex 原生扫描项目级 `.agents/skills`，Claude 经 `.claude/skills` 软链接读同一份——**一份文件，零复制**。总纲同理：`AGENTS.md` 一份，`CLAUDE.md` 用 `@AGENTS.md` 导入。

## 安全

- 私有仓库。**零明文密钥**——所有凭证走 1Password，仓库内只存 `op://` 引用。
- 详见 `AGENTS.md` §5 与 `inventory/credentials.md`。
