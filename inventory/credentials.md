---
last_verified: 2026-05-30
verified_by: human
source: "结构占位，待建立 1Password 条目后填充引用"
status: placeholder
---

# 凭证引用映射（credentials）

> 🔒 **铁律：本文件零明文密钥。** 只登记 `op://` 引用，运行时用 `op read` / `op run` 解析。
> 当前多数凭证尚未录入 1Password（用户历史上复用同一弱密码），见 `docs/plans/` 与首个任务 `credential-rotation`。

## 约定

- 统一 Vault：**`HomeLab`**（已确认存在）。
- 引用格式：`op://HomeLab/<item>/<field>`。
- ⚠ **`op://` 引用不支持非 ASCII**：条目名为中文（如「主路由管理密码」）时，`op read` 报 `invalid character`。
  → 用**条目 ID**（`op item list --vault HomeLab` 可查）或给条目起 ASCII 名。
- SSH 走 1Password SSH Agent 转发（密钥条目 `Johnson (Ed25519)` 在 HomeLab vault），本地无私钥。

## 已录入（real）

| 用途 | op:// 引用 | 备注 |
|---|---|---|
| 主路由管理后台 | `op://HomeLab/kaxaao54c3iiibcwjd4wx2ehcm/password` | 中文条目「主路由管理密码」，仅密码登录；用 item-id 引用 |
| Nginx Proxy Manager | `op://HomeLab/Nginx Proxy Manager/password` | 用户已录入（ASCII 名，可直接用）|
| SSH 私钥 | `op://HomeLab/Johnson (Ed25519)` | 1Password SSH Agent 使用 |

## 引用表（待填充 — 现为占位）

| 用途 | 类型 | op:// 引用（占位） | 暴露级别 | 状态 |
|---|---|---|---|---|
| 联想百应 系统账户 | SSH/登录 | 走 1Password SSH Agent | 内网/认证链路 P1 | TODO |
| 1Panel 后台 | web | `op://HomeLab/1panel/password` | 公网邻接 P0 | 待录入 |
| PVE root | web/ssh | `op://HomeLab/pve/password` | 公网邻接 P0 | 待录入 |
| QNAP 管理 | web | `op://HomeLab/qnap/password` | 公网邻接 P0 | 待录入 |
| Emby | web | `op://HomeLab/emby/password` | 公网可达 P0 | 待录入 |
| Nginx Proxy Manager | web | `op://HomeLab/npm/password` | 公网邻接 P0 | 待录入 |
| AdGuardHome | web | `op://HomeLab/adguardhome/password` | 内网 P2 | 待录入 |
| DNS 服务商 API token（泛域名 LE） | token | `op://HomeLab/dns-api/credential` | **高危·控制域名** | 待录入 |
| v2fly / vmess 凭证 | secret | `op://HomeLab/vmess/uuid` | **高危·入内网** | 待录入 |
| ddns-go 后台 | web | `op://HomeLab/ddns-go/password` | 公网邻接 P0 | 待录入 |
| Surge（如有订阅/密钥） | secret | TODO | 本机 | TODO |

> 暴露级别参见 `policies/guardrails.md`。P0/高危项在 `credential-rotation` 中**优先**录入并轮换为唯一强密码。

## 用法示例

```bash
# 解析单个字段
op read "op://HomeLab/npm/password"

# 注入环境变量执行（推荐，不落盘）
op run --env-file=<(echo 'NPM_PW=op://HomeLab/npm/password') -- some-command
```
