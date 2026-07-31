---
date: 2026-07-31
operator: ai
affected: [homeassistant, dashboard-ha]
risk: low
status: success
guardrails: []
---

# 接入并验证 dashboard-ha 书房窗帘控制

## 授权与范围

用户明确授权真实接入和测试书房窗帘。本次写入严格限定为：

- `cover.shu_fang_sha_lian`（书房纱帘）；
- `cover.wai_ci_wo_zhe_guang_lian`（书房遮光帘）。

未对客厅或其他房间的窗帘执行任何写入。

## 执行

1. 通过 Home Assistant REST API 只读核验两个实体的 ID、`friendly_name`、当前位置和
   `set_cover_position` 能力。
2. 依次将两幅窗帘从 100% 调到 90%，等待 HA 状态确认后恢复到 100%。
3. 通过 dashboard-ha 的实际 live 页面读取两个 100% 状态。
4. 使用页面滑杆将书房纱帘调到 90%，确认 HA 推送后页面显示 90%，再用页面打开按钮恢复到 100%。
5. 最终再次通过 REST API 确认两幅窗帘均为 `open`、`current_position: 100`。

## 结果

- 两个真实实体的位置控制与恢复均成功。
- dashboard-ha 的配置、服务调用、HA 状态推送和 UI 更新链路正常。
- 两幅窗帘最终均恢复到测试前的 100%。
- 未修改 Home Assistant 配置、服务、容器或持久化数据，inventory 无需变更。
