---
last_verified: 2026-05-30
verified_by: human          # 用户口述，AI 尚未连接核实
source: "用户对话补充（2026-05-30），未经设备实连核实"
status: unverified
---

# 设备清单（devices）

> ⚠️ 本表为用户口述的稳定事实，AI **尚未实连核实**。`status: unverified`。
> 首次 `inventory-reconcile`（只读）后改为 `verified`。
> 标 `TODO` 的字段是用户未提供、需补全的。

## 服务器 / NAS

| 设备 | 型号 | CPU/内存/存储 | 固定 IP | 网口 | 位置 | 电源 | 角色 |
|---|---|---|---|---|---|---|---|
| QNAP | TS-264C | — / — / 16TB 希捷银河企业氦气盘 | 192.168.8.10 | 2.4G ⚠️ | 客厅电视柜 | 施耐德 BK650M2-CH UPS | 存储 + Emby |
| 联想百应 NUC | (百应 N100) | N100 / 8G / 256G | 192.168.8.15 | 2.4G ⚠️ | 书房 | TODO | Debian + 1Panel，主力 Docker / 网络服务 |
| 极摩客 NUC | (N100) | N100 / 16G / 512G | 192.168.8.16 (PVE 管理页) | 2.4G ⚠️ | 书房 | TODO | PVE 实验机 |
| Mac mini | M4 万兆版 | M4 / 16G / 256G + 1TB 外置(尿袋) | 192.168.8.18 | 万兆 | 书房 | TODO | **运维中枢** + Surge 网关 |

## 影音 / 终端

| 设备 | 型号 | 固定 IP | 网口 | 位置 |
|---|---|---|---|---|
| 索尼电视 | K-85XR70 | 192.168.8.12 | 千兆 | 客厅 |
| Apple TV 4K | — | TODO（DHCP?） | 千兆 | 客厅电视柜 |

## SSH 接入（已验证：来自 `~/.ssh/config`，2026-05-30）

全局走 1Password SSH Agent（`Host *` → `IdentityAgent .../1password/.../agent.sock`），本地无私钥。

| 别名 | 设备 | 地址 | 用户 | 端口 |
|---|---|---|---|---|
| `n100` | 联想百应 NUC | 192.168.8.15 | `johnson` | 22 |
| `jonas` | QNAP | 192.168.8.10 | `Johnson`（大写） | 22 |
| — | 极摩客 PVE | 192.168.8.16 | ⚠ 待确认 | 22 |
| 本机 | Mac mini | 192.168.8.18 | `liyongsheng` | — |

> 注：「ssh config 里有」≠「连得通」。首次只读连通后再把对应设备标 `verified`。

## 待核实 / 待补 (TODO)

- ⚠️ **网口速率"2.4G"** 为用户原话，疑为 **2.5GbE**，实连后核实并改正。
- 各服务器内存/电源接法、Apple TV IP、QNAP CPU 等空缺字段。
- UPS 仅给 QNAP 供电？其它设备是否有 UPS / 后备？
- 设备序列号 / MAC（如需）。

## 动态事实（不在此固化，实连时拉取）

- 实际在线状态、固件/系统版本、磁盘 SMART/温度、CPU/内存占用 → 见各 `*-ops` skill 或 `inventory-reconcile`。
