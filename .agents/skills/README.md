# skills（.agents/skills）

本目录是项目 skill 的**唯一真身存放处**，Claude Code 与 Codex 共享。

## 双工具发现机制（已实测，2026-05-30，codex 0.135.0）

- **Codex**：向上扫描项目级 `.agents/skills`，自动加为 skill root（实测列为 `r6`）。
- **Claude Code**：通过仓库内软链接 `.claude/skills → ../.agents/skills` 发现同一份。

→ **一份文件，零复制，零漂移。** 不要在 `.claude/` 或别处再放第二份。

## 一个 skill 的结构

```
.agents/skills/<name>/
├── SKILL.md          # 必需：frontmatter(name, description) + 步骤正文
├── scripts/          # 可选：确定性脚本，优先复用而非重写
├── references/       # 可选：长文档，按需加载
└── assets/           # 可选：模板/资源
```

`SKILL.md` frontmatter 最简形式：

```yaml
---
name: skill-name
description: 一句话说清"做什么 + 何时触发"（两个工具都靠它决定是否调用）
---
```

## 原则

- **从被验证过的操作里长出来**：第一次和 AI 跑通某操作 → 蒸馏成 skill，别预先臆想。
- 每个 skill 只管一件事；引用 `policies/guardrails.md` 的规则 id；密钥用 `op://`。
- 改动后两个工具都需重启/重载才会刷新 skill 列表。

## 计划中的第一批（地基）

`homelab-access` · `record-operation` · `inventory-reconcile` · `credential-rotation`
（详见 `docs/plans/2026-05-30-homelab-ai-ops-design.md`）
