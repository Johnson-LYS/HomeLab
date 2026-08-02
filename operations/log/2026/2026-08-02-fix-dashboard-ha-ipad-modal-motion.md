---
date: 2026-08-02
operator: ai
affected: [n100, dashboard-ha]
risk: low
status: success
guardrails: [CONFIRM, PRE-04]
---

# 修复 Dashboard HA iPad 弹层动效（20260802-185540）

## 现象

用户反馈天气弹层在 iPad Safari 中瞬间出现，没有设计系统规定的过渡动画；桌面浏览器正常，且同一台 iPad 上 Floorplan 灯组动画正常。已确认 iPad 未启用系统“减弱动态效果”。

## 原因判断

灯组动画运行在常驻 DOM 上，而天气与温湿度弹层由 React Aria Portal 临时挂载。原实现仅在短暂的 `data-entering` 状态存在时声明进入动画。自动化 WebKit 能观察到该状态，但真机 iPad Safari 在 Portal 挂载、滚动锁定和 backdrop 合成发生于同一首帧时，可能直接绘制最终状态。

## 执行

- 将天气与温湿度弹层的进入动画改为挂载后的默认动画，不再依赖短暂的 `data-entering` 属性。
- 保留 `data-exiting` 退出动画。
- 为弹层增加 `will-change`、`translateZ(0)` 和背面隐藏，明确建立 opacity/transform 合成层。
- 保留全局 `prefers-reduced-motion: reduce` 行为。
- 增加回归断言：`data-entering` 消失后，天气弹层仍保持 `dialog-enter` 与 280ms 动效定义。
- 构建并部署 `linux/amd64` 镜像 `dashboard-ha:20260802-185540`。
- 镜像 ID：`sha256:1b3610a21eb015ef28d5a3bb45eb8a499015016de4819db64b39a0c699da4d54`。
- 切换前备份 Compose 为 `/opt/1panel/docker/compose/dashboard-ha/compose.yaml.backup-20260802-185540`。
- 旧镜像 `dashboard-ha:20260802-175138` 保留用于回滚。

## 验证

- iPad WebKit E2E：通过。
- `pnpm check`：11 个测试文件、81 项测试全部通过，类型检查、ESLint 和生产构建通过。
- 本地修复镜像：healthy，HTTP 200，产物包含默认 `dialog-enter` 动画与合成层样式。
- n100 容器：running、healthy，内网与局域网 HTTP 均为 200。
- 线上 CSS：`/assets/index-BdhfmDZm.css`，确认包含兼容样式。
- 真机 iPad Safari 的视觉效果尚待用户复测。
- 测试过程未调用任何 HA 写入或设备控制操作。

## 回滚

恢复备份 Compose 并重建容器：

```bash
ssh n100 '
  cd /opt/1panel/docker/compose/dashboard-ha
  sudo cp compose.yaml.backup-20260802-185540 compose.yaml
  docker compose up -d
'
```

回滚目标镜像为 `dashboard-ha:20260802-175138`。本次未删除旧镜像或备份文件。

## 影响

- `dashboard-ha` 容器因镜像切换被重建一次。
- 天气及温湿度弹层采用更稳健的进入动画触发方式。
- 未修改 Home Assistant、NPM、DNS、路由器或其他容器。
