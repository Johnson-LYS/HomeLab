---
last_verified: 2026-05-30
verified_by: human
source: "用户对话补充（2026-05-30），未经核实"
status: unverified
---

# 服务清单（services）

> ⚠️ 用户口述，AI 尚未核实。版本/容器列表等动态事实不在此固化，实连时拉取。

## 联想百应 NUC · Debian (192.168.8.15) — 主力

> ✅ 已只读核实（2026-05-30，`ssh n100 'docker ps; ss -tln'`）。1Panel 管理 30+ docker 服务。
> 端口为宿主发布端口（`host net` = 容器用主机网络，无独立映射）。内存 7.5Gi、nvme 233G 用 67%。

### 网络 / 接入（多为 P0 安全关键）
| 服务 | 端口 | 作用 | 备注 |
|---|---|---|---|
| Nginx Proxy Manager | :80 :81 :443 | 反向代理 + 泛域名 LE | `*.jsho.top` 反代入口 |
| AdGuardHome | :53(DNS) :3003(admin) :8443 :853 | 私有 DNS | 全网解析依赖；`*.jsho.top`→内网 |
| ddns-go | host net | 动态 DNS | `portal.jsho.top`→家庭公网 IP |
| v2fly | :13142 | vmess 加密代理回家 | **公网暴露面** |
| **wg-easy (WireGuard)** | :60085/tcp :60086/udp | **VPN 入内网** | ⚠ 新发现的第三条远程接入通道 |
| sub-store | :3001 | 代理订阅管理 | |

### 智能家居
| 服务 | 端口 | 作用 |
|---|---|---|
| Home Assistant | host net | 智能家居中枢（2026.3） |
| zigbee2mqtt | :8080 | Zigbee 网关 |
| z2m-mqtt (mosquitto) | :1883 | MQTT broker |
| matter-server | host net | Matter |
| scrypted | host net | 摄像头/NVR。server **0.143.0**（2026-05-31 升级自 0.137）；镜像 `ghcr.io/koush/scrypted:lite`（原 `1ms.run` 源已失效）。⚠ lite 无 Python/ML → OpenVINO 物体检测插件无法加载；要用 N100 核显做检测需改 `:intel` 变体（透传 /dev/dri）。无 Watchtower，手动升级 |
| node-red | host net | 自动化流 |

> Zigbee 设备清单（33 个 + 协调器）见 [`inventory/iot.md`](iot.md)。

### 媒体 / 信息
| 服务 | 端口 | 作用 |
|---|---|---|
| immich (server/ml/redis/pg) | :2283 | 照片管理（⚠ 数据卷位置待确认） |
| freshrss | :1236 | RSS |
| homepage | :3006 | 导航页 |
| sun-panel | :3002 | 导航页 |

### 自动化 / 数据 / 监控 / AI
| 服务 | 端口 | 作用 |
|---|---|---|
| n8n | :5678 | 工作流自动化 |
| qinglong | :5700 | 定时脚本面板 |
| nocodb | :8081 | 无代码数据库 |
| monitor: grafana / prometheus | :3000 / :9090 | 监控（AI 运维可复用） |
| database-postgres (pg17) | :5432 | 共享数据库 |
| teslamate (+grafana/api) | :4000 / :3004 / :8082 | 特斯拉行车记录 |
| new-api | :30001 | AI API 网关 |
| bark-server | :8787 | 推送通知（可用于告警） |
| 基础: postgres15 / redis | 内部 | 多服务依赖 |

> 1Panel 本体管理端口尚未在 docker 列表体现（1Panel 自身非容器或用别的端口），待确认。
> 完整端口与随机高位端口（21064-21101 等，疑 HA/HomeKit/matter）未逐一登记。

## 极摩客 NUC · PVE `pve` (192.168.8.16) — ✅ 已只读核实 2026-05-30

PVE 9.1.1（kernel 6.17，uptime 153 天）。管理页 `https://192.168.8.16:8006`。N100 4核/15Gi/512G。

### 虚拟机（12 个，多为实验，按需开关）
| VMID | 名称 | 状态 | 内存 | 说明 |
|---|---|---|---|---|
| 102 | **fnOS** | ▶ **running** | 2G | 虚拟化 NAS（飞牛 OS）——唯一常开 VM |
| 100 | win11 | stopped | 8G | |
| 101 | zorinOS | stopped | 8G | |
| 103 | uos | stopped | 8G | |
| 1111 | Minecraft | stopped | 12G | |
| 109/110 | istoreos / immortalwrt | stopped | — | 软路由实验 |
| 其余 | xp/freedos/templeOS/ubuntu/debian | stopped | — | 实验 |

LXC：`moltbot`(10001, stopped)。

### 存储
| 名称 | 类型 | 用量 | 备注 |
|---|---|---|---|
| local | dir | 39% (37/94G) | ISO/备份 |
| local-lvm | lvmthin | 19% | VM 磁盘 |
| **qnap_ssd** | **nfs** | 24% | ⚠ **NFS 挂自 QNAP SSD 卷 → PVE 依赖 QNAP 在线** |

## QNAP TS-264C `jonas` (192.168.8.10) — ✅ 已只读核实 2026-05-30

| 服务 | 作用 | 备注 |
|---|---|---|
| Emby | 媒体服务 | ⚠ 不在 docker（`docker: command not found`）→ 很可能是 **QPKG 原生应用**，安装路径/端口待确认 |
| 存储 | 见 `devices.md` QNAP 存储 | 16T(DataVol1 77%) + NVMe(SSD 24%)；**单盘无冗余 = 单点风险** |

> QTS（Linux 5.10.60-qnap）。SMART 属性需 root；阵列 `md2 [U]` 在线。
> 未发现 Container Station docker（该用户无 docker 权限或未装），Emby 走 QPKG 概率大。

## Mac mini M4 (192.168.8.18)

| 服务 | 作用 | 备注 |
|---|---|---|
| Surge（增强模式） | 科学上网 + **VM 网关模式** | 作为其它设备网关提供翻墙 |
| Claude Code / Codex | **运维中枢** | 本仓库工作目录 |

## 依赖关系（关键）

- 新增一个对外内网服务通常要同时动三处：**部署(1Panel/docker) → NPM(反代+证书) → AdGuardHome(解析)**。→ 未来 `publish-service` skill。
- 内网 DNS 依赖 AdGuardHome（在 .15）；**.15 宕机会影响全网解析**。
- 全家翻墙依赖 Mac mini Surge 网关；**动它可能全网断代理**。
- **PVE → QNAP**：PVE 的 `qnap_ssd` 存储是挂自 QNAP 的 NFS；**QNAP 宕机 / 重启会影响 PVE 上用该存储的 VM**（含常开的 fnOS）。

## TODO

- 1Panel 上的 Docker 服务逐一登记（名称、域名、端口、数据卷位置）。
- 各管理后台地址与端口补全。
- 公网实际可达的服务清单（结合防火墙/端口转发）。
