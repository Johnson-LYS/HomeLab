---
date: 2026-07-25
operator: ai
affected: [homeassistant, repository]
risk: low
status: success
guardrails: []
---

# 按 Home Assistant 实体调整香山府户型面板

## 目的

依据运行中 Home Assistant 的真实灯光与开关实体，移除尚未智能化房间的控制入口，并将厨房改为单灯直接控制。

## 只读核对

通过 Home Assistant 开发者工具模板页只读核对：

- 主卧：3 个 `light` 实体和夜灯 `switch` 实体。
- 厨房：现有单成员灯组 `light.chu_fang_deng_zu`。
- 公卫、客厅、餐厅、玄关、洗手台：均已有可复用灯组。
- 主卫、次卧、书房、阳台：没有对应的房间灯实体。

未读取或写入密码、token、Cookie 或其它凭证。

## 调整

- 主卫、次卧、书房、阳台不再显示亮灯图层、控制按钮或 Subview。
- 厨房直接绑定现有单成员灯组，长按打开更多信息，不再创建 Subview。
- 公卫、客厅、餐厅、玄关、洗手台改用 HA 中的真实灯组及成员实体。
- 主卧保留用户已填写的 4 个实体，并改为支持 `light`/`switch` 混合成员的通用 `group`。
- 全屋开关动作改用 `homeassistant.turn_on` / `homeassistant.turn_off`。
- 同步调整 README 与本地演练页。

## 验证

- Dashboard 与配置片段 YAML 语法检查通过。
- Dashboard 仅保留 7 个可控区域和 5 个多灯 Subview。
- 未保留待隐藏房间的示例实体或导航路径。
- 本地演练页与 Dashboard 的可控区域一致。

## 影响

- 仅修改仓库内的待部署源码。
- 未写入 n100，未修改运行中的 Home Assistant，未重启服务。
- 因运行环境事实未变化，本次不更新 `inventory/`。

## 后续

- [ ] 人工确认后备份并部署到 Home Assistant。
- [ ] 部署前运行 HA 配置检查。
- [ ] 部署完成后更新 `inventory/services.md` 并追加实际部署记录。
