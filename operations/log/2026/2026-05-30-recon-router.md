---
date: 2026-05-30
operator: ai
affected: [main-router]
risk: low
status: success
guardrails: [AUTO, RED-03]
---

# 主路由只读盘点（无头浏览器）

## 目的
主路由（ZTE 星云全屋主路由 MAX）web-only，用无头浏览器只读登录，盘点接入设备 + 公网入站暴露面（填 network.md 安全 TODO）。

## 执行
- 工具：`browser-use`（无头 Chromium）。后台 `http://192.168.8.1`，仅密码登录。
- 密码：`op read 'op://HomeLab/<item-id>/password'` 内联注入，输出抑制（不进上下文/仓库）。
- 浏览：接入设备（4 页 27 台）→ 应用/端口转发 → 应用/UPnP。**全程只读，未点任何保存/应用（RED-03）**。
- 结束 `browser-use close`，清理截图。

## 结果
- **接入设备 27 台**：全 MAC+IP+名称已入 `network.md`。确认 n100/.15、Mac/.18、QNAP/.10、PVE/.16、fnOS/.11、mesh 子节点 TL-XDR3040/.107 的 MAC。
- **端口转发仅 2 条**（均 → n100 .15）：v2fly 13142、wireguard 60086。**无 80/443 转发**。
- **UPnP 已启用**，动态映射：Syncthing 42666→.11:22000、ZeroTier。

## 关键发现 / 安全
- ✅ NPM 反代服务**非直接公网可达**（无 80/443 forward），对外仅经隧道。
- ⚠ **UPnP 开启** → 内网设备可自开公网口（Syncthing 已自开）。建议评估关闭。
- ⚠ 新发现 **ZeroTier**（第 4 个 overlay 网络）+ **Syncthing**(fnOS) + 2 个摄像头 IPC1/2。
- ⚠ op:// 不支持中文条目名 → 已记入 `credentials.md` 规范，改用 item-id。

## 回滚
纯只读，无配置更改，无需回滚。

## 影响
- `network.md`：新增「公网入站暴露面（实测）」+「接入设备快照 27 台」。
- `credentials.md`：新增「已录入」表（路由器/NPM/SSH）+ 中文条目名规范。

## 后续
- [ ] 评估关闭 UPnP（或限制）。
- [ ] 定位 ZeroTier 运行位置与用途。
- [ ] 核实「未知设备」.60/.254 是否自有。
- [ ] 摄像头 IPC1/2(.50/.51) 厂商/固件（安防设备需关注）。
