@AGENTS.md

<!-- 以上 @AGENTS.md 导入了唯一真相源（总纲）。以下仅为 Claude Code 专属补充。 -->

## Claude Code 专属说明

- **skills 发现**：`.claude/skills` 是指向 `../.agents/skills` 的软链接，真实 skill 都在 `.agents/skills/`。新增/修改 skill 一律改 `.agents/skills/`，不要在 `.claude/` 下另建。
- **机械护栏**：权限白名单 / hooks 写在 `.claude/settings.json`（团队共享）或 `.claude/settings.local.json`（本机，不提交）。把"红线/需确认"中能机械拦截的，落到这里强制执行。
- 其余一切（黄金法则、连接模型、密钥规则、文档维护、当前阶段）以 `AGENTS.md` 为准。
