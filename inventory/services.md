---
last_verified: 2026-05-30
verified_by: human
source: "用户对话补充（2026-05-30），未经核实"
status: unverified
---

# 服务清单（services）

> ⚠️ 用户口述，AI 尚未核实。版本/容器列表等动态事实不在此固化，实连时拉取。

## 联想百应 NUC · Debian (192.168.8.15) — 主力

| 服务 | 作用 | 访问 | 备注 |
|---|---|---|---|
| 1Panel | 面板，管理 Docker 应用 | TODO 管理地址/端口 | 上面部署了"很多服务"，待逐一登记 |
| Docker apps | 各类自托管服务 | 经 NPM 反代 *.jsho.top | TODO 清单 |
| ddns-go | 动态 DNS | — | 解析 `portal.jsho.top` → 家庭公网 IP |
| v2fly | 加密代理回家 | vmess 协议 | **公网暴露面，P0 安全关键** |
| AdGuardHome | 私有 DNS | TODO | 解析 `*.jsho.top` 到内网；全网 DNS |
| Nginx Proxy Manager | 反向代理 | TODO | 域名反代 + 泛域名 Let's Encrypt |

## 极摩客 NUC · PVE (192.168.8.16)

| 服务 | 作用 | 访问 | 备注 |
|---|---|---|---|
| Proxmox VE | 虚拟化实验平台 | https://192.168.8.16:8006 (待核实) | "做实验"用，VM 增删频繁 |

## QNAP TS-264C (192.168.8.10)

| 服务 | 作用 | 备注 |
|---|---|---|
| Emby | 媒体服务 | 唯一对外服务 |
| 存储 | 16TB 单盘 | ⚠️ 单盘无冗余，备份策略待定 |

## Mac mini M4 (192.168.8.18)

| 服务 | 作用 | 备注 |
|---|---|---|
| Surge（增强模式） | 科学上网 + **VM 网关模式** | 作为其它设备网关提供翻墙 |
| Claude Code / Codex | **运维中枢** | 本仓库工作目录 |

## 依赖关系（关键）

- 新增一个对外内网服务通常要同时动三处：**部署(1Panel/docker) → NPM(反代+证书) → AdGuardHome(解析)**。→ 未来 `publish-service` skill。
- 内网 DNS 依赖 AdGuardHome（在 .15）；**.15 宕机会影响全网解析**。
- 全家翻墙依赖 Mac mini Surge 网关；**动它可能全网断代理**。

## TODO

- 1Panel 上的 Docker 服务逐一登记（名称、域名、端口、数据卷位置）。
- 各管理后台地址与端口补全。
- 公网实际可达的服务清单（结合防火墙/端口转发）。
