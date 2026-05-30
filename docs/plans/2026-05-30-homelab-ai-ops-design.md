# HomeLab AI 运维 · 架构设计

- 日期：2026-05-30
- 状态：已确认（brainstorming 全程逐段确认）
- 作者：用户 + Claude（Opus 4.8）

## 1. 目标与定位

把家里一组服务器/NAS/网络设备的运维，从手动迁移到 **AI 运维**。
本仓库 = AI 的「运维大脑」，由 **Claude Code 与 Codex 共同**驱动。

- **终极目标：C（自主运维）**——AI 自主巡检、授权范围内自动修复。
- **起步阶段：A + 辅助执行**——AI 诊断/出方案，人确认/执行。
- A→C 不是重写架构，而是收紧 `policies/guardrails.md`（把操作从"需确认"下移到"自动放行"）。

### 为什么用「项目」而不是只建若干 skill

AI 运维需要四类知识，配合才有价值，单独的 skill 只覆盖其一：

| 类别 | 目录 | 性质 |
|---|---|---|
| ① 有什么 | `inventory/` | 事实，持续覆盖更新 |
| ② 怎么做 | `.agents/skills/` | 能力（skills） |
| ③ 发生过什么 | `operations/` | 历史，只追加 |
| ④ 不能碰什么 | `policies/` | 安全边界 |

git 历史本身就是运维审计日志；一个仓库能让四类知识互相引用、版本化、可移植。

## 2. 关键决策

### 2.1 连接与执行模型

- **中枢**：Mac mini（192.168.8.18，万兆/常开/Surge 网关）。
- **SSH**：统一走 1Password SSH Agent 转发，本地不落地私钥。
- **Web 服务**：各自 HTTP API / 管理页面（1Panel、PVE、AdGuardHome、NPM、ddns-go）。
- 仓库可移植（笔记本/Mac mini 皆可），因为**仓库内零敏感信息**。

### 2.2 密钥管理（核心安全决策）

- **1Password 是唯一密钥源，仓库零明文。** 仓库内只放 `op://` 引用，运行时 `op read`/`op run` 解析。
- 决策依据（红队结论）：
  1. **AI 项目特殊性**——仓库会被整体读入 AI 上下文，明文密钥会随每次对话外流（prompt/转录/缓存/服务商日志）。`op://` 引用让 AI 只见指针，密钥仅在命令执行瞬间materialize。
  2. **git 历史永久**——一次误提交即永久泄露，私有 ≠ 加密。
  3. **可移植放大风险**——可移植 + 明文 = 最坏组合（笔记本会丢/会上公网）。
  4. **"都是内网"不成立**——vmess、DNS API token、被 NPM 反代出去的服务都桥接内外网。
- 分级：高危/桥接内外（vmess、DNS token、各后台）必走 1Password；纯内网低危也建议 1Password，至少加密落库；非密（IP/拓扑/端口）明文进仓库。
- 待办：用户历史上复用同一弱密码且多未入 1Password → 首个任务 `credential-rotation`（先**录入**不改密码、再按暴露面**分批轮换**）。1Password 主密码须强密码 + 2FA（单点）。
- 依赖 `op` CLI（**当前未安装**，待装）。

### 2.3 双工具兼容（Claude + Codex）

**已实测（2026-05-30，codex-cli 0.135.0）**，结论：单一真身 + 双向发现，零复制。

- **总纲**：`AGENTS.md` 唯一真相源（Codex 直接读）；`CLAUDE.md` 仅一行 `@AGENTS.md` 导入（+ Claude 专属补充）。
- **skills**：真身只在 `.agents/skills/`。
  - Codex 向上扫描项目级 `.agents/skills`，自动加为 skill root（`codex debug prompt-input` 实测列为 `r6 = .../HomeLab/.agents/skills`，并从中发现测试 skill）。
  - Claude Code 经仓库内软链接 `.claude/skills → ../.agents/skills` 发现同一份（已在会话 skills 列表出现验证）。
  - 软链接随 git/GitHub 正常同步（mode 120000），Mac/Linux clone 还原；仅 ZIP 下载/Windows 检出失效（本场景不涉及）。
- **踩坑记录**：官方网页文档称 Codex 路径为 `.agents/skills`，但本机 0.135.0 的 user 级路径同时含 `~/.codex/skills` 与 `~/.agents/skills`；**以本机实测为准**。版本演进可能再变，新机器首次用 `codex debug prompt-input | grep "Skill roots"` 复核。

## 3. 文档体系（防腐烂）

- **事实分两类**：稳定（硬件/位置/布线/电源，手维护）vs 动态（IP/容器/版本/磁盘——不固化数值，存"怎么拉"+带时间戳快照）。
- 每个 `inventory/` 文件带溯源头：`last_verified` / `verified_by` / `source` / `status`。
- **黄金法则（闭环铁律）**：任何改状态的操作，同一次提交里 ① 更新 inventory ② 追加 `operations/log`。
- **对账兜底**：`inventory-reconcile` skill 定期拉实况 diff inventory，捕捉绕过 AI 的手动改动；到 C 阶段变定时巡检。
- 格式：表格 / 小 YAML 块，便于 diff。

## 4. operations 与 policies

- `operations/log/YYYY/YYYY-MM-DD-<slug>.md`，只追加。模板见 `operations/log/TEMPLATE.md`。价值：审计 + **AI 的学习语料**（动手前翻历史避坑）。
- `operations/postmortems/`：故障复盘，预防措施常沉淀为新 guardrail/skill。
- `policies/guardrails.md`：四级（🔴红线 / 🟠前置条件 / 🟡需确认 / 🟢自动放行），每条带 id。**这是 A→C 的旋钮**；晋升依据是 log 里的成功记录；红线永不晋升。两层护栏：guardrails.md（意图）+ `.claude/settings.json`（机械强制）。

## 5. skills 清单

**生长原则**：skill 从被验证过的操作里长出来，不预先臆想。

### 第一批 · 地基（建议先建）
| skill | 管什么 |
|---|---|
| `homelab-access` | 唯一"怎么连"入口：SSH 目标/用户、各服务 API base、从 1Password 解凭证 |
| `record-operation` | 落实闭环铁律：动手前读 inventory+guardrails，做完脚手架式生成 log 条目 |
| `inventory-reconcile` | 对账/巡检雏形：拉实况 → diff inventory → 报不一致 |
| `credential-rotation` | 第一个真实任务：凭证录入 1Password + 分级轮换；过程顺便建 inventory |

### 第二批 · 各平台（首次用到时再长出，不预建）
`1panel-ops` · `pve-ops`（先快照） · `qnap-ops`（16T 盘 SMART/Emby） · `dns-ops`/`reverse-proxy-ops`/`ddns-ops`（P0 对外） · `proxy-ops`（v2fly + Surge 网关，红线级）

### 第三批 · 走向 C
`publish-service`（部署→NPM→AdGuard→验证） · `patrol`（定时全栈巡检=自主巡检本体） · `backup-verify`（单盘兜底）

## 6. 起步路径

0. **搭骨架**（本次完成）：目录 + 软链接 + AGENTS/CLAUDE + 双工具发现验证。
1. **灌入初始事实 + 先立红线**：inventory 已起草（unverified）；guardrails 红线已立。
2. **建 `homelab-access` + 跑 `credential-rotation`**（A+辅助，端到端验证闭环）。
3. **`inventory-reconcile`（AI 首次碰设备，纯只读）** 校准 inventory，积累信任。
4. **按需长出第二批 skill + 沿 guardrail 旋钮爬坡到 C。**

晋升依据：操作在 `operations/log` 被 AI 成功做过 N 次、无意外——**用证据给信任**。

## 7. 待办（开工前/中）

- [x] 安装并登录 1Password CLI（`op` 2.34.0，会话已激活，2026-05-30）。
- [ ] 确认 1Password Vault 名（暂定 `HomeLab`；现有 vault：AiC / Private / 日冕，无 HomeLab）。
- [ ] 补全 inventory 的 TODO（网关 IP、网口真实速率"2.4G"?2.5GbE、1Panel 服务清单、公网暴露面/端口转发）。
- [ ] 建第一批地基 skill。
- [ ] 把可机械化的红线/确认项落到 `.claude/settings.json`。
