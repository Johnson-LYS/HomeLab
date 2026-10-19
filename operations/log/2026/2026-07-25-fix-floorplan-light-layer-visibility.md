---
date: 2026-07-25
operator: ai
affected: [homeassistant, repository]
risk: low
status: success
guardrails: []
---

# 修复户型面板亮灯图层常亮

## 只读核对

- HA 中 8 个绑定实体均能返回正常的 `on` / `off` 状态。
- 核对时主卧、厨房、餐厅、玄关和洗手台为 `off`，但其图层仍以
  `filter: none`、`opacity: 1` 渲染。
- 由此确认灯光实体本身正常，问题位于图片元素的 `state_filter` 未生效。

## 调整

- 将 8 个图片元素的 `state_filter` 透明度切换改为 HA 原生
  `conditional` 元素。
- 每个房间仅在对应灯光实体状态为 `on` 时挂载亮灯图片。
- 保留普通透明图层与 `screen` 混合图层原有的层级和定位。
- README 同步记录当前图层显示模型。

## 验证

- `floorplan-dashboard.yaml` YAML 语法检查通过。
- 8 个亮灯图片均由各自实体的 `state: "on"` 条件控制。
- 待用户把更新后的卡片 YAML 保存到现有 Dashboard 后进行运行态验证。

## 影响

- 仅修改仓库内待部署源码。
- 未修改或重启运行中的 Home Assistant。
- 运行环境事实未变化，不更新 `inventory/`。
