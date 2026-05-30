# HomeLab AI 运维 · 操作总纲（AGENTS.md）

> 这是本项目的**唯一真相源**。Codex 直接读本文件；Claude Code 通过 `CLAUDE.md` 的 `@AGENTS.md` 导入本文件。
> 任何 AI 在本仓库内执行运维操作前，**必须**先读完本文件。

## 1. 这个项目是什么

把一组家庭服务器 / NAS / 网络设备的运维，从「手动」迁移到「AI 运维」。
本仓库是 AI 的**运维大脑**：它同时承载四类知识——

| 类别 | 目录 | 性质 |
|---|---|---|
| ① 有什么 | `inventory/` | 环境的**事实**，会被持续覆盖更新（永远反映"现在"） |
| ② 怎么做 | `.agents/skills/` | 可复用的**能力**（skills），双工具共享 |
| ③ 发生过什么 | `operations/` | **历史**：操作记录 + 故障复盘，只追加不修改 |
| ④ 不能碰什么 | `policies/` | **安全边界**，约束一切自动化 |

**终极目标：C（自主运维）**——AI 自主巡检、在授权范围内自动修复。
**当前阶段：A + 辅助执行**（见 §8）。从 A 安全爬到 C 靠的是收紧 `policies/guardrails.md`，不是改架构。

## 2. 黄金法则（闭环铁律）

> **任何改变设备/服务状态的操作，必须在同一次提交里：**
> **① 更新受影响的 `inventory/` 文件；② 向 `operations/log/` 追加一条记录。**

这条法则把四个目录串成闭环，是文档不腐烂的根本机制。inventory 不靠"记得维护"，而是被引发它变化的操作顺手改掉。

## 3. 动手前必读顺序

1. 读 `policies/guardrails.md` —— 确认本次操作不踩红线、是否需人工确认。
2. 读相关 `inventory/` —— 搞清环境现状、该连哪台、有什么依赖。
3. 翻 `operations/log/` 近期记录 —— 看这台机器/这类操作历史上有没有坑。
4. 若已有对应 skill（`.agents/skills/`），按它执行。

## 4. 连接与执行模型

- **中枢**：Mac mini（`192.168.8.18`，万兆、常开、Surge 网关）。运维优先在此执行。
- **SSH**：统一走 **1Password SSH Agent 转发**，本地不落地私钥。
- **Web 服务**：通过各自 HTTP API / 管理页面操作（1Panel、PVE、AdGuardHome、Nginx Proxy Manager、ddns-go 等）。
- 具体主机、端口、API 入口见 `inventory/`。

## 5. 密钥处理（铁律）

- **1Password 是唯一密钥源。仓库里零明文密钥。**
- 仓库中只出现 **`op://` 引用**（见 `inventory/credentials.md`），运行时用 `op read` / `op run` 在命令执行的瞬间解析。
- **绝不**把真实密码、token、密钥写进任何被 git 跟踪的文件——它们会进 git 历史、也会进 AI 上下文。
- 1Password 主密码本身必须强密码 + 2FA（它是单点）。
- 依赖 1Password CLI：`op`。若未安装，先安装并 `op signin`。

## 6. 安全护栏

- 完整规则见 **`policies/guardrails.md`**，按 `红线 / 前置条件 / 需人工确认 / 自动放行` 四级。
- 该文件就是 A→C 的调节旋钮：信任增长 → 把操作从"需确认"挪到"自动放行"，依据是 `operations/log` 里它被成功做过、没意外。**红线永不晋升。**
- 机械层护栏在 `.claude/settings.json`（权限白名单 / hooks），不可被绕过。

## 7. 文档维护规则

- **事实分两类**：稳定事实（硬件/位置/布线/电源，手维护）；动态事实（实时 IP/容器/版本/磁盘，**不固化数值**，写明"怎么拉"+ 带时间戳的快照）。
- 每个 `inventory/` 文件带溯源头：`last_verified` / `verified_by`(human|ai) / `source`。腐烂即可见。
- 事实用**表格或小 YAML 块**，不用大段散文——人和 AI 都好 diff。
- `inventory/` 可覆盖更新；`operations/` 只追加不改。

## 8. 当前自动化阶段：A + 辅助执行

- AI 可：只读诊断、查状态、读日志、生成命令、起草记录。
- 改动类操作：AI 给出方案与命令，**由人确认/执行**；AI 负责写 `operations/log`。
- 推进到 B/C 的唯一方式：编辑 `policies/guardrails.md`。

## 9. skills 约定（双工具共享）

- 真实 skill 唯一存放处：**`.agents/skills/<name>/SKILL.md`**（frontmatter 含 `name`/`description`）。
- **Codex**：原生向上扫描项目级 `.agents/skills`（实测为 skill root `r6`）。
- **Claude Code**：通过 `.claude/skills → ../.agents/skills` 软链接发现同一份。
- 因此：**一份文件，零复制，零漂移。** 别在别处再放第二份。
- skill **从被验证过的操作里长出来**，不预先臆想：第一次和 AI 一起跑通某操作 → 把那套流程蒸馏成 skill。

## 10. 目录地图

```
HomeLab/
├── AGENTS.md            # 本文件（唯一真相源）
├── CLAUDE.md            # @AGENTS.md + Claude 专属补充
├── README.md           # 人看的入口
├── .agents/skills/     # ② skills（Codex 原生 / Claude 软链接）
├── .claude/skills      # → ../.agents/skills（软链接）
├── inventory/          # ① 事实：devices / network / services / credentials
├── operations/         # ③ 历史：log/ + postmortems/
├── policies/           # ④ 护栏：guardrails.md
└── docs/plans/         # 设计文档
```
