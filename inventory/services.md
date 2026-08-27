---
last_verified: 2026-08-27
verified_by: ai
source: "用户对话补充（2026-05-30）+ AI 只读/变更核实（2026-06-14，ssh n100 docker/ss/chrony/go2rtc）+ AI 变更核实（2026-06-18，n100 哪吒 agent 清理；2026-06-30，部署 ham-a-exam-trainer 静态站点；2026-07-02，更新 ham-a-exam-trainer 静态内容并验证 ham.jsho.top，release 20260702-114908 / 20260702-161851 / 20260702-225749；2026-07-04，脚本化更新 release 20260704-002336；2026-07-05，脚本化更新 release 20260705-214009；2026-07-10，部署 Mac mini screen-sharing-control launchd 服务；2026-07-22，共享 PostgreSQL 17.6→18.4 与 TeslaMate 栈升级；Home Assistant 2026.3.1→2026.7.3；2026-08-12，ali99 TeslaMate 独立迁入 n100；2026-08-14，部署 FRP；2026-08-24，ali99 Nginx/HTTPS 与 FMO Activity FRP STCP；2026-08-27，统一 app.bi8syn.com 路径）"
status: partial
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
| homelab-ntp | :123/udp | 内网 NTP | 系统级 `chrony.service`，监听 `192.168.8.15:123/udp`，允许 `192.168.8.0/24`；Docker 版已清理 |
| ddns-go | host net | 动态 DNS | `portal.jsho.top`→家庭公网 IP |
| v2fly | :13142 | vmess 加密代理回家 | **公网暴露面** |
| **wg-easy (WireGuard)** | :60085/tcp :60086/udp | **VPN 入内网** | ⚠ 新发现的第三条远程接入通道 |
| sub-store | :3001 | 代理订阅管理 | |

### 智能家居
| 服务 | 端口 | 作用 |
|---|---|---|
| Home Assistant | host net | 智能家居中枢；Core **2026.7.3**，镜像固定为 `docker.1ms.run/homeassistant/home-assistant:2026.7.3`；Recorder 使用共享 PostgreSQL 18.4 |
| zigbee2mqtt | :8080 | Zigbee 网关 |
| z2m-mqtt (mosquitto) | :1883 | MQTT broker |
| matter-server | host net | Matter |
| scrypted | host net | 摄像头/NVR。server **0.143.0**（2026-05-31 升级自 0.137）；镜像 `ghcr.io/koush/scrypted:lite`（原 `1ms.run` 源已失效）。⚠ lite 无 Python/ML → OpenVINO 物体检测插件无法加载；要用 N100 核显做检测需改 `:intel` 变体（透传 /dev/dri）。无 Watchtower，手动升级 |
| go2rtc | :1984 :8554 :8555/tcp+udp | 摄像头流网关 / restream。1Panel compose: `/opt/1panel/docker/compose/go2rtc`；配置 `data/go2rtc.yaml`；无独立 backup sidecar，依赖 1Panel 系统快照备份打包 compose 目录 |
| node-red | host net | 自动化流 |

> Zigbee 设备清单（33 个 + 协调器）见 [`inventory/iot.md`](iot.md)。

### 媒体 / 信息
| 服务 | 端口 | 作用 |
|---|---|---|
| immich (server/ml/redis/pg) | :2283 | 照片管理（⚠ 数据卷位置待确认） |
| freshrss | :1236 | RSS |
| homepage | :3006 | 导航页 |
| sun-panel | :3002 | 导航页 |
| ham-a-exam-trainer | :18080 | 业余无线电 A 证刷题静态站点；Docker 容器 `ham-a-exam-trainer`；站点目录 `/home/johnson/sites/ham-a-exam-trainer/www`；NPM 待配置反代 |

### 自动化 / 数据 / 监控 / AI
| 服务 | 端口 | 作用 |
|---|---|---|
| n8n | :5678 | 工作流自动化 |
| qinglong | :5700 | 定时脚本面板 |
| nocodb | :8081 | 无代码数据库 |
| monitor: grafana / prometheus | :3000 / :9090 | 监控（AI 运维可复用） |
| database-postgres (pg18) | :5432 | 共享数据库；PostgreSQL **18.4**，承载 Home Assistant / NocoDB / TeslaMate；生产卷 `database_postgres18-data`，旧 PG17 卷保留用于回滚 |
| teslamate (+grafana/api) | :4000 / :3004 / :8082 | 特斯拉行车记录；TeslaMate/Grafana **4.0.1**，TeslaMateAPI **1.25.0** |
| teslamate-ali99（独立栈） | :4001 / :3005 / :8083 / :1884 | 2026-08-12 从 `ali99` 迁入，与原栈完全隔离；TeslaMate **2.1.1**、Grafana、TeslaMateAPI、Mosquitto、独立 PostgreSQL **17.6**；Compose `/home/johnson/teslamate-ali99`，数据库 `teslamate_kjh`，源端容器/卷停机保留用于回滚 |
| new-api | :30001 | AI API 网关 |
| bark-server | :8787 | 推送通知（可用于告警） |
| 基础: postgres15 / redis | 内部 | 多服务依赖 |

> 哪吒 agent：2026-06-18 已从 n100 移除；本机 Mac mini 与 QNAP `jonas` 未发现哪吒探针。

> 1Panel 本体管理端口尚未在 docker 列表体现（1Panel 自身非容器或用别的端口），待确认。
> 完整端口与随机高位端口（21064-21101 等，疑 HA/HomeKit/matter）未逐一登记。

## 极摩客 NUC · PVE `pve` (192.168.8.16) — ✅ 已只读核实 2026-08-24

PVE 9.1.1（kernel 6.17，uptime 153 天）。管理页 `https://192.168.8.16:8006`。N100 4核/15Gi/512G。

### 虚拟机（12 个，多为实验，按需开关）
| VMID | 名称 | 状态 | 内存 | 说明 |
|---|---|---|---|---|
| 103 | **FMO** | ▶ **running** | 4G | FMO 相关服务 |
| 107 | **server** | ▶ **running** | 4G | Debian 13；IP `192.168.8.131`；FRP client 与 FMO Activity；2026-08-24 变更前快照 `pre-frp-web-20260824` |
| 102 | **fnOS** | stopped | 2G | 虚拟化 NAS（飞牛 OS） |
| 100 | win11 | stopped | 8G | |
| 101 | zorinOS | stopped | 8G | |
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
| screen-sharing-control | :18765/tcp 关闭本机 `Screen Sharing.app` 的内网 HTTP 控制服务 | 用户 `launchd` 服务 `com.jsho.homelab.screen-sharing-control`；监听 `192.168.8.18:18765`；要求 bearer token；token 仅在 Mac mini 本地 `~/Library/Application Support/HomeLabScreenSharingControl/token`，不入库；不使用 Docker |

## 阿里云主机 `ali99` (8.138.130.141)

| 服务 | 端口 | 作用 | 备注 |
|---|---|---|---|
| FRP Server (`frps`) | `:7000/tcp`（控制）、`:13122/tcp`（代理） | 接收 `server` 的主动连接并公开其 SSH | **v0.69.0**；systemd `frps.service`；配置 `/etc/frp/frps.toml`；强制 TLS、Wire Protocol v2；仅允许代理端口 13122 |
| FRP STCP Visitor (`frpc-visitor`) | `127.0.0.1:18088` | 私下接入 `server` 的 FMO Activity | **v0.69.0**；systemd `frpc-visitor.service`；配置 `/etc/frp/frpc-visitor.toml`；不新增公网远端端口 |
| Nginx | `:80/tcp`、`:443/tcp` | FMO 静态页与 Activity 公网 HTTPS 入口 | Debian 原生 **1.22.1**；配置 `/etc/nginx/sites-available/fmo-sites.conf`；统一静态入口 `app.bi8syn.com/fmo-companion/privacy/`，根文件 `/fmo-companion/privacy/index.html`；旧子域名 308 跳转；原 Caddy 容器停机保留 |
| acme.sh | systemd timer | Let's Encrypt TLS-ALPN 签发与自动续期 | **v3.1.4**；`acme-fmo-renew.timer` 每日检查；证书覆盖 `app.bi8syn.com`、`fmo-companion.bi8syn.com`、`fmo-activity.bi8syn.com`；因阿里云未备案 HTTP 拦截，不使用 HTTP-01 |

## `server` (192.168.8.131)

| 服务 | 本地/远端端口 | 作用 | 备注 |
|---|---|---|---|
| FRP Client (`frpc`) | `127.0.0.1:22` → `ali99:13122/tcp`；`192.168.8.131:18088` → STCP | 经阿里云公网入口访问本机 SSH，并向 `ali99` 私下提供 FMO Activity | **v0.69.0**；systemd `frpc.service`；配置 `/etc/frp/frpc.toml`；主动连接 `ali99:7000`；SSH 密码认证已关闭；STCP secret 复用本地 FRP token 文件且不入仓库 |

## 依赖关系（关键）

- 新增一个对外内网服务通常要同时动三处：**部署(1Panel/docker) → NPM(反代+证书) → AdGuardHome(解析)**。→ 未来 `publish-service` skill。
- 内网 DNS 依赖 AdGuardHome（在 .15）；**.15 宕机会影响全网解析**。
- 全家翻墙依赖 Mac mini Surge 网关；**动它可能全网断代理**。
- **PVE → QNAP**：PVE 的 `qnap_ssd` 存储是挂自 QNAP 的 NFS；**QNAP 宕机 / 重启会影响 PVE 上用该存储的 VM**（含常开的 fnOS）。
- **server → ali99**：`server` 的公网 SSH 入口依赖两端 FRP systemd 服务和 `ali99` 的 TCP 7000/13122 可达；家庭路由器无需端口转发。
- **FMO Activity → 公网**：`server:18088` → FRP STCP → `ali99:127.0.0.1:18088` → Nginx `fmo-activity.bi8syn.com:443`；18088 不直接暴露公网。

## TODO

- 1Panel 上的 Docker 服务逐一登记（名称、域名、端口、数据卷位置）。
- 各管理后台地址与端口补全。
- 公网实际可达的服务清单（结合防火墙/端口转发）。
