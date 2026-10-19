---
last_verified: 2026-10-19
verified_by: ai
source: "用户对话补充（2026-05-30）+ FRP 公网路径端到端核实（2026-08-14）+ FMO HTTPS/FRP STCP 公网路径核实（2026-08-24）+ app.bi8syn.com 统一路径核实（2026-08-27）+ 新 FRP 网关/ali99-2 端到端核实（2026-10-19）"
status: partial
---

# 网络拓扑与 IP（network）

> ⚠️ 用户口述，AI 尚未核实。户型：三室两厅；仅**客厅**与**主卧**有网线。
> 运营商：电信，**动态公网 IP**（光猫桥接，主路由拨号）。

## 拓扑

```
[电信] ─ 光猫(桥接, 弱电箱/玄关柜)
          │
   主路由 中兴星云 MAX(硬路由, 拨号, 弱电箱)  ── 网段 192.168.8.0/24
          │
        傻瓜交换机 S1(弱电箱)
          ├── TP-Link XDR3040 #主(mesh 主, 提供 WiFi)
          ├── 客厅 网线 ──→ 电视柜 傻瓜交换机 S3
          │                   ├── TP-Link XDR3040 #子(mesh 子)
          │                   ├── 索尼电视 K-85XR70 (192.168.8.12, 千兆)
          │                   ├── Apple TV 4K (千兆)
          │                   └── QNAP (192.168.8.10, 2.4G⚠️)
          ├── 主卧 网线
          └── 隐形光纤(10G) ──→ 书房 傻瓜交换机 S2
                                 └── 联想百应/FRP 网关/Mac mini（书房设备）
```

- **全链路电口均为 2.4G⚠️（疑为 2.5GbE）**；隐形光纤虽 10G，瓶颈在电口。
- Mesh：两台 TP-Link XDR3040（同型号），S1 下挂 #主，S3 下挂 #子。

## 固定 IP 分配（在主路由分配）

| IP | 设备 | 备注 |
|---|---|---|
| 192.168.8.1 | 主路由 中兴星云 MAX | TODO 待核实网关 IP |
| 192.168.8.10 | QNAP | |
| 192.168.8.12 | 索尼电视 K-85XR70 | |
| 192.168.8.15 | 联想百应 NUC (Debian) | 1Panel/网络服务主力 |
| 192.168.8.18 | Mac mini M4 | 运维中枢 + Surge 网关 |
| 192.168.8.198 | FRP 网关设备 | Debian 13；向 `ali99-2` 主动建立 FRP 控制通道 |

## 接入设备快照（主路由，27 台，2026-05-30）

> 来源：主路由后台「接入设备/在线设备」（无头浏览器只读）。DHCP 动态事实，IP/在线随时变；
> 刷新需重登后台。所有设备从主路由视角均显示"有线接入"（经交换机/ mesh 回程）。

**基础设施 / 服务器**
| 设备 | IP | MAC |
|---|---|---|
| Lenovo-N100（n100·Debian 主力） | .15 | 00:e0:4c:71:80:07 |
| Mac mini（中枢） | .18 | d0:11:e5:a1:cf:d6 |
| NAS（QNAP·jonas） | .10 | 24:5e:be:83:45:88 |
| FRP 网关设备 | .198 | TODO |
| fnOverQnap（fnOS VM） | .11 | 52:54:00:77:fe:8a（QEMU）|
| TL-XDR3040 易展版（mesh 子节点） | .107 | 74:39:89:ac:0d:a5 |

**影音**：SonyTV `.12`、Apple TV 4K `.113`、Apple HomePod 5 ×3（`.137/.183/.158`）

**智能家居（非 Zigbee / Wi-Fi 类）**
| 设备 | IP | 备注 |
|---|---|---|
| lumi-gateway-v3 | .111 | Aqara/米家网关 |
| yeelink-light-lamp15 | .38 | Yeelight 灯 |
| uplus-haier | .112 | 海尔家电 |
| NarwalRobotics | .188 | 云鲸扫地机 |
| Magic-Switch-S1E | .110 | |
| tg7100c / Bouffalolab | .103 / .179 | BL602 Wi-Fi 模组 |

**摄像头**：IPC1 `.50`、IPC2 `.51`（MAC 80:ae:54:*）

**终端**：iPhone ×2（`.163/.180`）、iPad `.186`、联想 K6 Note `.104`、[本机]`.162`（访问后台的 Mac，随机 MAC）

**未知**：未知设备-B76F `.60`、未知设备-22E0 `.254`（建议核实是否自有设备）

> ⚠ 多台 Apple/手机为**随机 MAC**（locally-administered），非固定身份。

## 域名 / 对外

- 主域名：`jsho.top`
- 公网入口：`portal.jsho.top`（ddns-go 动态解析到家庭公网 IP）
- 内网服务：`*.jsho.top`，由 AdGuardHome 解析到内网，Nginx Proxy Manager 反代 + 泛域名 Let's Encrypt。
- FMO 公网域名：`app.bi8syn.com`、`fmo-companion.bi8syn.com`、`fmo-activity.bi8syn.com`，A 记录均指向 `ali99` (`8.138.130.141`)。

### 阿里云 FRP 入口（2026-08-14 实测）

| 公网地址 | 协议 | 目标 | 用途 |
|---|---|---|---|
| `8.138.130.141:7000` | TCP + TLS | `ali99` 的 `frps` | `server`（192.168.8.131）主动出站建立 FRP 控制通道 |
| `8.138.130.141:13122` | TCP | `server` 的 `127.0.0.1:22` | 公网 SSH 入口；仅 SSH 密钥认证 |

- 家庭主路由未新增端口转发；该链路不依赖 NAT 打洞。
- `frps` 的 `allowPorts` 仅允许远端代理端口 `13122`。

### 新 FRP 应用入口（2026-10-19 实测）

| 公网地址 | 协议 | 目标 | 用途 |
|---|---|---|---|
| `47.109.85.53:7000` | TCP + TLS | `ali99-2` 的 `frps` | `frp`（192.168.8.198）主动建立控制通道 |
| `ali99-2:127.0.0.1:18000-18099` | TCP，仅回环 | FRP 代理端口池 | 供 `ali99-2` 本机 Nginx 反代未来部署在 n100 的应用 |

- `frp` 的客户端可将 `192.168.8.15:<应用端口>` 映射到上述回环端口池；家庭路由器无需端口转发。
- `frps.proxyBindAddr = "127.0.0.1"`，应用映射端口不会直接暴露公网。
- 控制通道使用 FRP v0.71.1、强制 TLS、Let's Encrypt 证书校验与独立 64 字符 Token；Token 仅从 1Password 投放到两端受限文件。
- 首次验收曾临时映射 `n100:22` 到 `ali99-2:127.0.0.1:18000`，两端 SSH 主机指纹一致；验收后该代理已停用，18000 不再监听。

### FMO 公网 HTTPS 入口（2026-08-27 实测）

| 公网入口 | `ali99` 处理 | 后端 |
|---|---|---|
| `https://app.bi8syn.com/fmo-companion/privacy/` | 宿主机 Nginx 静态文件 | `/fmo-companion/privacy/index.html` |
| `https://fmo-companion.bi8syn.com/privacy/` | Nginx 308 跳转 | `https://app.bi8syn.com/fmo-companion/privacy/` |
| `https://fmo-activity.bi8syn.com/` | Nginx → `127.0.0.1:18088` | FRP STCP → `192.168.8.131:18088` |

- STCP visitor 仅监听 `ali99:127.0.0.1:18088`，没有新增公网 18088 端口；家庭路由器无需端口转发。
- 三个域名共用一张 Let's Encrypt 证书，acme.sh 使用 TLS-ALPN 自动续期；HTTP-01 会被阿里云 `Non-compliance ICP Filing` 页面拦截。
- 公网浏览器已实测两个 HTTPS 页面正常；80/tcp 仍可能被阿里云备案策略返回 403，客户端应直接使用 HTTPS。

### 公网入站暴露面（主路由实测 2026-05-30，无头浏览器只读）

**显式端口转发（仅 2 条，均 → n100 .15）：**
| 名称 | 协议 | 广域网端口 | → 内网 |
|---|---|---|---|
| v2fly | TCP+UDP | 13142 | 192.168.8.15:13142 |
| wireguard | TCP+UDP | 60086 | 192.168.8.15:60086 |

**UPnP（⚠ 已启用，内网设备可自行开公网口）当前动态映射：**
- Syncthing：TCP/UDP `42666 → 192.168.8.11:22000`（fnOS VM）
- ZeroTier：UPnP 列表中有映射（overlay VPN）

**关键结论 / 安全提示：**
- ✅ **无 80/443 端口转发** → NPM 反代的内网服务**并非直接公网可达**，对外仅经隧道（v2fly / WireGuard / ZeroTier）。比预想更安全。
- ⚠ **UPnP 已开**：任意内网设备可自行打开公网端口（Syncthing 已自开 42666）。建议评估关闭 UPnP，改按需手动端口转发。
- ⚠ 新发现 **ZeroTier**（第 4 个 overlay 网络）——需定位运行位置与用途。
- 当前真实入站口 = v2fly(13142) + WireGuard(60086) + UPnP 动态(Syncthing 42666 / ZeroTier)。

> 主路由后台：ZTE「星云全屋主路由 MAX」，`http://192.168.8.1`，仅密码登录（`op://HomeLab/<主路由管理密码 item-id>/password`）。**RED-03：只读，禁改。**

## TODO

- 主路由/网关 IP、各 mesh 节点管理 IP、交换机是否网管型。
- DHCP 池范围；Apple TV 等 DHCP 设备地址。
- 防火墙 / 端口转发规则（公网暴露面清单）—— **安全关键，需专门梳理**。

## VMess 接入故障核实（2026-09-27）

```yaml
last_verified: 2026-09-27
verified_by: ai
source: n100 的 Fail2ban/SSH 轮转日志、iptables、容器连通性检查及 Surge 固定 VMess 请求
```

| 项目 | 已核实事实 |
|---|---|
| 容器网络 | v2fly `10.8.8.4`、WireGuard `10.8.8.2`、ADH `10.8.8.3`，同属 `portal-network_adguardhome` |
| Fail2ban sshd | 检查时 `maxretry=5`、`findtime=300`、`bantime=-1`；INPUT 的所有 TCP 都进入 `f2b-sshd`，不只 SSH |
| 代理源地址 | 经 VMess 连接 n100 SSH 时，sshd 看到的来源为 `10.8.8.4`，认证失败会导致共享代理出口被封 |
| SSH 避免多密钥失败 | MacBook 使用 `IdentitiesOnly=yes` 和 `~/.ssh/github-johnson-1password.pub` 指定 Johnson (Ed25519)，签名仍由 1Password Agent 完成；此次未改全局 SSH 配置 |
| 解封后快照 | 用户手动解封，2026-09-27 11:02 CST 查询 sshd 当前封禁数为 0；固定 VMess 访问两个 HTTPS 域名和 `.15:3006` 均为 200 |
| 刷新方法 | `sudo fail2ban-client status sshd`、`sudo iptables -S INPUT`、`sudo iptables -S f2b-sshd`；用 Surge 单次请求指定 VMess 复测 |

操作记录：`operations/log/2026/2026-09-27-vmess-fail2ban-unban.md`。
