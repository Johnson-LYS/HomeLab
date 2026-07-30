---
date: 2026-07-30
operator: ai
affected: [homeassistant, dashboard-ha]
risk: low
status: success
guardrails: []
---

# 验证 dashboard-ha 玄关灯控制

## 授权与范围

用户明确允许自动化测试读取全部设备，但写入测试只能操作
`light.xuan_guan_deng_zu`。本次未对其他实体执行写操作。

## 执行

1. 通过 dashboard-ha 的真实 HA WebSocket 连接确认玄关灯组初始状态为 `on`。
2. 通过前端调用 `light.turn_off`，等待 HA 实体推送确认按钮与 Floorplan 图层均变为关闭。
3. 通过前端调用 `light.turn_on`，等待 HA 实体推送确认按钮与图层恢复开启。

## 结果

- 玄关灯组已恢复测试前的 `on` 状态。
- 前端动作、HA 状态推送、按钮状态和 Floorplan 图层保持一致。
- 未修改 Home Assistant 配置、服务、容器或持久化数据。
- 未产生持久环境变化，因此 inventory 无需变更。
