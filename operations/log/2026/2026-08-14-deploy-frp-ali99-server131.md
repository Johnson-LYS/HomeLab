---
date: 2026-08-14
operator: ai
affected: [ali99, server-192.168.8.131, frp]
risk: high
status: success
guardrails: [CONFIRM, PRE-03, PRE-04]
---

# 在 ali99 与 server/.131 间部署 FRP SSH 入口

## 目的与授权

- 用户要求以 `ali99` 为服务端、`johnson@192.168.8.131` 为客户端部署最新 FRP，并在查看准确端口与暴露范围后明确确认执行。
- 采用客户端主动出站的标准 TCP 代理，不修改家庭主路由，也不依赖 NAT 打洞。
- 回滚命令在启动服务前确定；131 原有局域网 SSH 入口保持不变，因此保留另一条管理路径，满足 PRE-03。

## 执行

1. 只读核实两端均为 x86_64 Debian + systemd；确认目标端口未占用，131 的 SSH 已关闭密码认证。
2. 从 FRP 官方 Release 获取 **v0.69.0** Linux amd64 包，并按官方 SHA-256 `6b90d1cd28fc661f170c0de90dde03d2c63e4fd7ce0ae2da2ca1c28014b8146e` 校验。
3. 在 1Password `HomeLab` vault 创建 `frp-ali99-131` Password 条目；仓库只记录 `op://HomeLab/frp-ali99-131/password`，没有写入或输出明文 token。
4. 在 `ali99` 安装 `/usr/local/bin/frps`，配置 `/etc/frp/frps.toml` 与 `frps.service`；监听 `7000/tcp`，强制 TLS，代理端口白名单仅含 `13122`。
5. 131 直连 GitHub 超时，因此由中枢下载、校验后通过 SSH 传送同一安装包；安装 `/usr/local/bin/frpc`，配置 `/etc/frp/frpc.toml` 与 `frpc.service`，将 `127.0.0.1:22` 映射到 `ali99:13122`。
6. 两端 token 文件均为 `frp:frp`、权限 `0400`；配置文件不含 secret。服务使用专用无登录 `frp` 用户和 systemd 安全限制，并设为开机自启。

## 验证

- `frps verify` 与 `frpc verify` 均报告配置语法正确。
- 两端版本均为 `0.69.0`，`frps.service` / `frpc.service` 均为 `active` + `enabled`。
- 服务端日志确认客户端版本 0.69.0 登录成功，代理 `server-ssh` 创建成功；监听 `*:7000` 与 `*:13122`。
- 从 Mac mini 实测 `8.138.130.141:7000`、`:13122` 均可建立 TCP 连接。
- 端到端执行 `ssh -p 13122 johnson@8.138.130.141` 成功，远端返回 `HOST=server USER=johnson VIA=frp`。

## 回滚

```bash
ssh johnson@192.168.8.131 'sudo systemctl disable --now frpc'
ssh ali99 'systemctl disable --now frps'
```

- 停止上述服务即可立刻关闭 FRP 通道，不影响两台机器原有 SSH 服务。
- 如需完全卸载，再经人工确认后删除对应 unit、配置、二进制和 1Password 条目；本次未执行删除。

## 影响

- 更新 `inventory/devices.md`：登记并核实 `server/.131` SSH 主机及 FRP 入口。
- 更新 `inventory/network.md`：登记阿里云 TCP 7000/13122 公网暴露面，明确家庭路由器未变更。
- 更新 `inventory/services.md`：登记 `frps`、`frpc` 版本、配置、端口和依赖关系。
- 更新 `inventory/credentials.md`：登记 FRP token 的 1Password 引用。
- 未修改主路由、Surge、DNS、NPM、Ali99 既有 Docker 服务或两端 sshd 配置。

## 后续

- 日常连接：`ssh -p 13122 johnson@8.138.130.141`。
- 升级 FRP 时先升级 `frps`，再升级 `frpc`，并重复配置校验和端到端 SSH 验证。
