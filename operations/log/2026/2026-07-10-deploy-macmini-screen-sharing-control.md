---
date: 2026-07-10
operator: ai
affected: [macmini, screen-sharing-control]
risk: low
status: success
guardrails: [CONFIRM, PRE-04]
---

# 部署 Mac mini 屏幕共享控制服务

## 目的
在 Mac mini 上提供一个受 token 保护的内网 HTTP 端点，收到请求后关闭当前用户的 macOS `Screen Sharing.app` 客户端连接。

## 执行
用户确认部署后，未采用 Docker：Docker Desktop 在 macOS 上运行于 Linux VM，无法自然控制宿主机图形会话，反而需要额外打洞或 SSH 回宿主。

实际采用用户级 `launchd` 服务：
- 源码入库：`scripts/screen-sharing-control-server.py`
- plist 模板入库：`scripts/com.jsho.homelab.screen-sharing-control.plist`
- 远端安装目录：`~/Library/Application Support/HomeLabScreenSharingControl/server.py`
- 远端 token 文件：`~/Library/Application Support/HomeLabScreenSharingControl/token`
- 远端 LaunchAgent：`~/Library/LaunchAgents/com.jsho.homelab.screen-sharing-control.plist`
- 监听地址：`192.168.8.18:18765`

关键命令摘要（未打印 token）：
```bash
scp -o BatchMode=yes -o ConnectTimeout=10 \
  scripts/screen-sharing-control-server.py \
  scripts/com.jsho.homelab.screen-sharing-control.plist \
  liyongsheng@192.168.8.18:/tmp/

ssh -o BatchMode=yes -o ConnectTimeout=10 liyongsheng@192.168.8.18 \
  'python3 -m py_compile /tmp/screen-sharing-control-server.py;
   plutil -lint /tmp/com.jsho.homelab.screen-sharing-control.plist;
   mkdir -p "$HOME/Library/Application Support/HomeLabScreenSharingControl" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs";
   cp /tmp/screen-sharing-control-server.py "$HOME/Library/Application Support/HomeLabScreenSharingControl/server.py";
   cp /tmp/com.jsho.homelab.screen-sharing-control.plist "$HOME/Library/LaunchAgents/com.jsho.homelab.screen-sharing-control.plist";
   chmod 700 "$HOME/Library/Application Support/HomeLabScreenSharingControl";
   chmod 600 "$HOME/Library/Application Support/HomeLabScreenSharingControl/server.py" "$HOME/Library/LaunchAgents/com.jsho.homelab.screen-sharing-control.plist";
   launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.jsho.homelab.screen-sharing-control.plist";
   launchctl kickstart -k "gui/$(id -u)/com.jsho.homelab.screen-sharing-control"'
```

注意：第一次安装尝试发现当前 Codex 本地 shell 并非 `192.168.8.18`（本地接口为 `192.168.6.86`），已移除该误装的本地 LaunchAgent 和本地 token，随后改用 SSH 在 Mac mini 上完成部署。

## 验证
远端服务状态：
```text
state = running
pid = 50440
```

监听端口：
```text
Python 50440 liyongsheng TCP 192.168.8.18:18765 (LISTEN)
```

带 token 健康检查：
```json
{"ok":true,"screen_sharing_running":true}
```

未授权访问验证：
```text
HTTP/1.0 401 Unauthorized
{"ok":false,"error":"unauthorized"}
```

本次验证未调用 `/close-screen-sharing`，因此没有主动断开当前屏幕共享连接。

## 回滚
在 Mac mini 上执行：
```bash
launchctl bootout "gui/$(id -u)/com.jsho.homelab.screen-sharing-control" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.jsho.homelab.screen-sharing-control.plist"
rm -f "$HOME/Library/Application Support/HomeLabScreenSharingControl/server.py"
rm -f "$HOME/Library/Application Support/HomeLabScreenSharingControl/token"
rmdir "$HOME/Library/Application Support/HomeLabScreenSharingControl" 2>/dev/null || true
```

## 影响
- 新增 `scripts/screen-sharing-control-server.py`
- 新增 `scripts/com.jsho.homelab.screen-sharing-control.plist`
- 更新 `inventory/services.md`：登记 Mac mini `screen-sharing-control`
- 追加本日志

## 后续
- 可在 iOS 快捷指令 / Home Assistant / 其他内网设备中配置 `POST http://192.168.8.18:18765/close-screen-sharing`，请求头带 `Authorization: Bearer <token>`。
- 如需多设备使用，建议把 token 存进 1Password 后由各端手动配置，仍不写入仓库。
