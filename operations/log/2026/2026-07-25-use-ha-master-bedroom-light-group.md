---
date: 2026-07-25
operator: ai
affected: [homeassistant, repository]
risk: low
status: success
guardrails: []
---

# 户型面板改用 HA 内建主卧灯组

## 只读核对

用户已在运行中的 Home Assistant 创建 `light.zhu_wo_deng_zu`（主卧灯组），成员为：

- `light.zhu_wo_lu_mi_e1_shuang_kong_left`
- `light.zhu_wo_lu_mi_e1_dan_kong`
- `light.zhu_wo_lu_mi_e1_shuang_kong_right`
- `light.ye_deng`

夜灯已经由 `switch.ye_deng` 转换为 `light.ye_deng`。上述事实通过 HA 开发者工具模板页只读核对。

## 调整

- Dashboard 的主卧组引用由 `group.master_bedroom_lights` 改为 `light.zhu_wo_deng_zu`。
- 主卧 Subview 的夜灯引用改为 `light.ye_deng`。
- 删除不再需要的 `light-groups-snippet.yaml`。
- README 不再要求向 `configuration.yaml` 或 `groups.yaml` 合并主卧组。
- 同步更新本地演练页的主卧实体引用。

## 验证

- Dashboard 与配置片段 YAML 语法检查通过。
- 待部署源码中不再引用旧组或 `switch.ye_deng`。
- 本地演练页保持 8 个可控区域。

## 影响

- 仅修改仓库内待部署源码。
- 未写入 n100，未修改或重启运行中的 Home Assistant。
- 运行环境事实未变化，不更新 `inventory/`。
