---
date: 2026-06-18
operator: ai
affected: [macmini, n100, jonas, nezha-agent]
risk: low
status: success
guardrails: [AUTO, CONFIRM, PRE-04]
---

# 移除 n100 哪吒监控探针

## 目的
检查本机、n100、QNAP 是否安装哪吒监控探针；如有则全部卸载。

## 前置
- 已读 `policies/guardrails.md`：只读检查属于 AUTO；停止/卸载服务属于 CONFIRM/PRE-04。
- 用户明确要求卸载所有发现的哪吒探针。
- 已只读确认：
  - 本机 Mac mini：未发现哪吒探针。
  - QNAP `jonas`：未发现哪吒探针。
  - n100：存在 3 个 systemd 哪吒 agent 服务。

## 1Password / 沙箱结论
在 Codex 沙箱内执行 `op account list` / `op vault list` 会报：
```
1Password CLI couldn't connect to the 1Password desktop app
```

同一命令提升出沙箱后可正常连接 1Password Desktop App，并能列出 `HomeLab` vault。结论：此前 `op` 失败是 Codex 沙箱隔离 App integration 通道，不是 1Password CLI 或桌面 App 本身不可用。

`HomeLab` vault 中存在 `n100` 条目，字段标签包含：
```
username
password
notesPlain
```

卸载时使用 `op://HomeLab/n100/password` 运行时读取密码，仅通过 stdin 传给远端 `sudo -S`，未打印、未写入文件。

## 执行
n100 上发现并卸载的 systemd 服务：
```
nezha-agent.service
nezha-agent-908ada1.service
nezha-agent-d2da91d.service
```

删除范围：
```
/etc/systemd/system/nezha-agent.service
/etc/systemd/system/nezha-agent-908ada1.service
/etc/systemd/system/nezha-agent-d2da91d.service
/etc/sysconfig/nezha-agent
/etc/sysconfig/nezha-agent-908ada1
/etc/sysconfig/nezha-agent-d2da91d
/opt/nezha/agent/nezha-agent
/opt/nezha/agent/config.yml
/opt/nezha/agent/config-isqll.yml
/opt/nezha/agent/config-ojglx.yml
/opt/nezha/agent
/opt/nezha
```

实际执行输出包含：
```
Removed "/etc/systemd/system/multi-user.target.wants/nezha-agent.service".
Removed "/etc/systemd/system/multi-user.target.wants/nezha-agent-d2da91d.service".
Removed "/etc/systemd/system/multi-user.target.wants/nezha-agent-908ada1.service".
```

`systemctl reset-failed` 对已删除 unit 返回 `Unit ... not loaded`，符合预期。

## 验证
n100：
```
pgrep -a -x nezha-agent
systemctl list-unit-files --no-pager | grep -i nezha
test -e /opt/nezha
docker ps -a --format ... | grep -Ei 'nezha|哪吒'
find /opt/1panel/docker/compose ... | xargs grep -IlEi 'nezha|哪吒'
```

结果：
- 无 `nezha-agent` 进程。
- 无哪吒 systemd unit / unit file。
- `/opt/nezha` 不存在。
- Docker / 1Panel compose 未发现哪吒引用。

本机 Mac mini：
- 无哪吒进程。
- 无哪吒 launchd 项。
- 常见安装路径未发现哪吒。

QNAP `jonas`：
- 无哪吒进程。
- 常见路径未发现哪吒。
- QPKG 未发现哪吒。

## 回滚
如需恢复，需要重新安装哪吒 agent，并重新登记服务端地址与密钥。原配置文件内容未读取、未写入仓库，避免泄露 agent token 或服务端地址。

## 影响
- n100 的 3 个哪吒 agent 已停止、禁用并删除。
- 本机 Mac mini 与 QNAP 未做状态改动。
- `inventory/services.md` 已记录哪吒 agent 清理状态。
