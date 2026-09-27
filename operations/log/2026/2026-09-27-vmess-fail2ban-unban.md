---
date: 2026-09-27
operator: human
affected: [n100, v2fly, fail2ban]
risk: medium
status: success
guardrails: [CONFIRM]
---

# 用户手动解除 v2fly 容器的 Fail2ban 封禁

## 诊断

- 从轮转日志 `/var/log/fail2ban.log.4.gz`、`/var/log/auth.log.4.gz` 查明：2026-09-01 12:41 至 12:52 CST 多次 SSH `Too many authentication failures`，12:54:13 两次密码认证失败；12:54:13.898 封禁 `10.8.8.4`。无法从代理后的来源地址确定原始客户端。
- 当前 sshd jail 为 5 分钟内 5 次失败、永久封禁；INPUT 所有 TCP 跳入 f2b-sshd。被封地址是 v2fly 容器，WireGuard 地址为 `10.8.8.2`，因此其访问不受这条规则影响。
- v2fly 5.30.0 配置校验通过，ADH 正确解析 jsho.top 为 192.168.8.15；v2fly 容器访问 `.15:3006` 被拒绝，而宿主机及 WireGuard 容器返回 200。
- AI SSH 改用单次连接参数 `-o IdentitiesOnly=yes -i ~/.ssh/github-johnson-1password.pub`，匹配 1Password Johnson (Ed25519)。未改全局 SSH 配置、未导出私钥。

## 执行与授权

用户明确报告已手动解封。AI 此前建议命令为 `sudo fail2ban-client set sshd unbanip 10.8.8.4`，但未观察用户实际执行方式；AI 未执行解封或修改 Fail2ban 规则。

## 验证

2026-09-27 11:02 CST：

- `fail2ban-client status sshd`：Currently banned=0，Banned IP list 为空。
- Surge 脚本单次请求显式指定 `🏠 香山府 VMESS`，不经智能组选路；`https://jsho.top/`、`https://n100.jsho.top/`、`http://192.168.8.15:3006/` 全部 HTTP 200、error=null。
- 解封前失败、解封后相同 VMess 路径成功，验证此次故障由封禁引起。

## 影响与后续

- 更新 inventory/network.md 对应核实快照，与本记录配套保留。
- Fail2ban 永久封禁及所有 TCP 的范围未改；长期策略调整需另行授权。
- 如确需重新封禁，可使用 `sudo fail2ban-client set sshd banip 10.8.8.4`，但会再次中断 VMess 到 n100 的访问，不能作为常规操作自动执行。
