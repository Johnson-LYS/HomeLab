---
date: 2026-09-27
incident_started: 2026-09-01T12:54:13+08:00
status: resolved
affected: [n100, v2fly, fail2ban]
source: SSH 与 Fail2ban 轮转日志、iptables、容器对比测试、固定 VMess 解封前后验证
---

# SSH 认证失败导致 VMess 共享出口被永久封禁

## 现象与影响

MacBook 经 Surge 回家访问 jsho.top 和内网 IP 失败，另一条 WireGuard 路径正常。Surge Home 智能组包含多条路径，自动选择或手动切换会使用户感知为间歇性恢复。仅观察页面恢复、节点测速或重启，不能证明 VMess 恢复。

已验证的故障范围是 v2fly 到 n100 的 TCP 服务访问；不应将其扩大为所有家庭设备或所有互联网目标均受同一规则影响。

## 根因与证据

1. SSH 经 VMess 连接 n100 时，服务端看到的来源是 v2fly 容器 10.8.8.4。
2. 2026-09-01 12:41 至 12:52 CST 多次出现 maximum authentication attempts exceeded / Too many authentication failures；12:54:13 又出现两次密码认证失败。
3. Fail2ban 在 12:54:13.898 执行 Ban 10.8.8.4。当前 sshd jail 配置为 maxretry=5、findtime=300、bantime=-1。
4. 实际 INPUT 规则将所有 TCP 送入 f2b-sshd，封禁并不限于 22 端口。由此连带阻断代理出口到 n100 的网页请求。
5. 容器内部 DNS 正常、配置校验通过；v2fly 访问 n100:3006 失败，同网络的 WireGuard 容器访问成功。
6. 用户手动解封后，固定 VMess 请求访问 jsho.top、n100.jsho.top 和 192.168.8.15:3006 均返回 HTTP 200，封禁列表为空。

原始客户端身份无法从代理后的源地址判断。多密钥尝试是合理触发机制，但日志不足以确定当时哪个客户端或程序提交了哪些错误身份。封禁早于本次诊断，不是本次诊断新建的封禁。

## 排查经验

- 先查看实际请求的 policyName 和连接日志，不凭策略组界面显示或测速结果判断路径。此次界面曾显示 DIRECT，但真实请求日志显示 VMess。
- TCP 建连成功不等于 VMess 端到端成功；服务端 default route Warning 表示选择默认出站，本身不是失败信息。
- 对齐同一次请求后，dispatcher 已记录目标地址说明请求进入分发阶段，应继续查出站与回程，而非反复更换 UUID 或 DNS。
- 从故障容器内测试 DNS、目标 IP 和端口，并与宿主机、正常容器对照；同一 Docker 网络不意味着各来源受到相同规则处理。
- 查 Fail2ban 时检查实际 iptables 跳转范围，不能由 jail 名 sshd 推断仅封 SSH。
- 当前日志为空时，继续查 .1、.gz 轮转日志；本次历史证据位于 fail2ban.log.4.gz 和 auth.log.4.gz。
- 不按短期节点测速成功下结论；用真实内网页面固定指定单一策略，进行修复前后对照。

## SSH 预防方法

本次已验证 MacBook 上以下连接方式可避免 Agent 依次尝试大量身份：

```sh
ssh -o IdentitiesOnly=yes \
  -i ~/.ssh/github-johnson-1password.pub \
  n100
```

该文件为与 1Password Johnson (Ed25519) 匹配的公钥，签名由已配置的 1Password SSH Agent 完成。公钥路径只在本机验证；其它电脑应先核实。未导出私钥，未修改全局 SSH 配置。

## 后续改进（未执行）

- 评估 sshd jail 是否应仅限制 SSH 端口，以及永久封禁是否符合家庭接入需求。
- 如考虑代理出口白名单，需权衡它会同时豁免该出口后的所有客户端，不能直接默认加入。
- 修复封禁通知失败的问题；日志记录邮件通知命令执行失败。
- 上述均属于独立配置变更，遵循 policies/guardrails.md，不能因本次解封自动视为已授权。

## 关联

- [操作记录](../log/2026/2026-09-27-vmess-fail2ban-unban.md)
- [网络事实与核实快照](../../inventory/network.md)
