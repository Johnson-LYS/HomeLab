---
date: 2026-06-18
operator: ai
affected: [macmini, n100, jonas, nezha-agent]
risk: low
status: superseded
guardrails: [AUTO, CONFIRM]
---

# 检查并准备卸载哪吒监控探针

## 目的
用户要求检查本机、n100、QNAP 是否安装哪吒监控探针；如有则全部卸载。

## 前置
- 已读 `policies/guardrails.md`：只读检查属于 AUTO；卸载软件属于 CONFIRM。
- 用户本轮已明确要求卸载。
- SSH 连接按 `homelab-access` skill 使用别名：`n100`、`jonas`。

## 执行
只读检查范围：
- 进程：`ps` 中 `nezha` / `哪吒`。
- 服务：macOS `launchd`、Linux `systemd`、QNAP QPKG。
- 常见路径：`/opt/nezha`、`/etc/systemd/system/nezha-agent*.service`、QNAP `.qpkg` 路径。
- Docker / Compose 中的 `nezha` / `哪吒` 相关容器或配置。

结果：
- 本机 Mac mini：未发现哪吒探针。
- QNAP `jonas`：未发现哪吒探针；`docker: not found`。
- n100：发现 3 个 root 级 systemd 探针正在运行：
  - `nezha-agent.service`
  - `nezha-agent-908ada1.service`
  - `nezha-agent-d2da91d.service`

n100 service 文件均指向同一个二进制：
```
/opt/nezha/agent/nezha-agent
```

配置文件：
```
/opt/nezha/agent/config.yml
/opt/nezha/agent/config-isqll.yml
/opt/nezha/agent/config-ojglx.yml
```

尝试确认 sudo 能力：
```
ssh n100 'sudo -n true'
```

结果：
```
sudo: a password is required
```

`inventory/credentials.md` 中没有 n100 系统账户 sudo 密码引用；`op item list --vault HomeLab` 当前也无法连接 1Password 桌面 App，因此 AI 无法在不接触明文密码的前提下完成卸载。

> 后续已确认 `op` 失败是 Codex 沙箱隔离 1Password Desktop App integration 所致；提升出沙箱后可运行时读取 `op://HomeLab/n100/password`，并已完成卸载。完成记录见 `operations/log/2026/2026-06-18-remove-nezha-agent.md`。以下命令为当时准备的人工方案，已不再需要执行。

## 当时准备的人工执行命令（已取代）
在 n100 上执行：
```
sudo systemctl disable --now nezha-agent.service nezha-agent-908ada1.service nezha-agent-d2da91d.service
sudo rm -f /etc/systemd/system/nezha-agent.service /etc/systemd/system/nezha-agent-908ada1.service /etc/systemd/system/nezha-agent-d2da91d.service
sudo rm -f /etc/sysconfig/nezha-agent /etc/sysconfig/nezha-agent-908ada1 /etc/sysconfig/nezha-agent-d2da91d
sudo rm -f /opt/nezha/agent/nezha-agent /opt/nezha/agent/config.yml /opt/nezha/agent/config-isqll.yml /opt/nezha/agent/config-ojglx.yml
sudo rmdir /opt/nezha/agent /opt/nezha
sudo systemctl daemon-reload
sudo systemctl reset-failed nezha-agent.service nezha-agent-908ada1.service nezha-agent-d2da91d.service
```

## 验证命令
执行后在 n100 验证：
```
systemctl list-units --all --type=service --no-pager | grep -i nezha || true
systemctl list-unit-files --no-pager | grep -i nezha || true
ps -ef | grep -Ei '[n]ezha|哪吒' || true
test ! -e /opt/nezha && echo '/opt/nezha removed'
```

## 回滚
本轮未执行卸载，设备状态未改变，无需回滚。

如后续人工执行了卸载，回滚需要重新安装哪吒 agent 并恢复原 3 个配置文件；当前 AI 没有读取配置内容，避免把服务端地址或密钥写入仓库和上下文。

## 影响
- 未改动本机、n100、QNAP 的运行状态。
- 未更新 `inventory/`：本轮只有只读检查和阻塞记录，没有完成设备状态变更。

## 后续
- [x] 已通过 `op://HomeLab/n100/password` 运行时解析完成卸载。
- [x] 已复跑验证命令，并另起完成日志：`operations/log/2026/2026-06-18-remove-nezha-agent.md`。
