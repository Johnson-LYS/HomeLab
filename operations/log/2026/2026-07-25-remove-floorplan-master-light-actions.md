---
date: 2026-07-25
operator: ai
affected: [homeassistant, repository]
risk: low
status: success
guardrails: []
---

# 移除户型面板全屋灯光按钮

## 调整

- 从 Floorplan Dashboard 卡片中移除“全部关闭”和“全部打开”按钮。
- 同步移除本地演练页中的全屋快捷按钮、样式和事件处理。
- 保留各房间灯光按钮、亮灯条件图层和实体映射。

## 验证

- Dashboard YAML 语法检查通过。
- Floorplan 源码中不再包含全屋开关动作。

## 影响

- 仅修改仓库内待部署源码。
- 未修改或重启运行中的 Home Assistant。
- 运行环境事实未变化，不更新 `inventory/`。
