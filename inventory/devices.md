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

| 别名 | 设备 | 地址 | 用户 | 端口 | 主机名 | OS | 状态 |
|---|---|---|---|---|---|---|---|
| `n100` | 联想百应 NUC | 192.168.8.15 | `johnson` | 22 | `debian-mini` | Debian Linux 6.1.0-37 | ✅ 已连通 2026-05-30 |
| `jonas` | QNAP | 192.168.8.10 | `Johnson`（大写） | 22 | `Jonas` | QNAP Linux 5.10.60-qnap | ✅ 已连通 2026-05-30 |
| — | 极摩客 PVE | 192.168.8.16 | ⚠ 待确认 | 22 | — | — | known_hosts 有，未连 |
| 本机 | Mac mini | 192.168.8.18 | `liyongsheng` | — | — | macOS（本机） | 运维在此本地执行 |

> 已连通 = 只读 `ssh <别名> 'hostname;whoami;uname -sr'` 成功（走 1Password Agent）。
> ⚠ n100 实际主机名为 `debian-mini`，与 ssh config 里另一个 `debian-mini`(192.168.6.252) 同名但非同机，注意区分。

## QNAP 存储（已只读核实 2026-05-30，`qcli_storage`）

| Port | 设备 | 容量 | 型号 | RAID | 卷 | 用量 |
|---|---|---|---|---|---|---|
| 1 | /dev/sda (3.5" SATA HDD) | 14.55 TB | **Seagate ST16000NM000J**（Exos 企业氦气） | md2 Single `[U]` | DataVol1 (`/share/CACHEDEV2_DATA`) | **77%**（11.0T/14.3T，剩 3.3T） |
| 3 | /dev/nvme0n1 (M.2 PCIe) | 465.76 GB | **ZHITAI Ti600 500GB** | md1 Single | SSD (`/share/CACHEDEV1_DATA`) | 24%（96G/402G） |

> 🔴 **单点风险（关联 RED-01）**：16T 为 **Single RAID 无冗余 + 唯一副本 + 已 77% 将满**。
> 属性级 SMART（`get_hd_smartinfo -d 1`）需 root（`Johnson` 无权，"Open device fail"）→ 暂只能确认阵列 `[U]` 在线，未能读重映射扇区/通电时长/温度。
> **行动建议**：① 尽快定备份策略（→ 未来 `backup-verify` skill）；② SMART 监控需 root 方案（QNAP GUI 或授权）。

## 待核实 / 待补 (TODO)

- ⚠️ **网口速率"2.4G"** 为用户原话，疑为 **2.5GbE**，实连后核实并改正。
- 各服务器内存/电源接法、Apple TV IP、QNAP CPU 等空缺字段。
- UPS 仅给 QNAP 供电？其它设备是否有 UPS / 后备？
- 设备序列号 / MAC（如需）。

## 动态事实（不在此固化，实连时拉取）

- 实际在线状态、固件/系统版本、磁盘 SMART/温度、CPU/内存占用 → 见各 `*-ops` skill 或 `inventory-reconcile`。
