---
date: 2026-07-25
operator: ai
affected: [homeassistant, repository]
risk: low
status: success
guardrails: []
---

# 恢复香山府户型面板的书房屏幕挂灯

## 更正

用户确认书房已有支持亮度和色温控制的屏幕挂灯。此前将书房归为“无对应房间灯实体”不准确，本记录追加更正，不修改既有历史日志。

运行中的 Home Assistant 已存在：

- 主灯：`light.yeelight_lamp15_0x304653f2`
- 背景灯：`light.yeelight_lamp15_0x304653f2_ambilight`

## 调整

- 恢复书房的亮灯图层和控制按钮。
- 主按钮绑定屏幕挂灯主灯实体。
- 单击切换主灯；长按打开更多信息，以调节亮度和色温。
- 背景灯暂不并入主按钮，避免切换主灯时同时改变背光。
- 将书房主灯加入全屋打开和全屋关闭。
- 同步更新 README 与本地演练页。

## 验证

- Dashboard 和配置片段 YAML 语法检查通过。
- Dashboard 保留 8 个可控区域、5 个多灯 Subview。
- 本地演练页包含 8 个按钮和 8 个亮灯图层，图片均可加载。

## 影响

- 仅修改仓库内待部署源码。
- 未写入 n100，未修改或重启运行中的 Home Assistant。
- 运行环境事实未变化，不更新 `inventory/`。
