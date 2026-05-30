---
date: 2026-05-30
operator: ai
affected: [n100]
risk: low
status: success
guardrails: [AUTO]
---

# 盘点 Zigbee IoT 设备（zigbee2mqtt）

## 目的
绝大多数 IoT 为 Zigbee，经 z2m 接入。从 z2m 取权威设备名册，建 `inventory/iot.md`。

## 执行
只读订阅 MQTT 保留主题（未发布、未改动）：
```
ssh n100 'docker exec z2m-mqtt-1 mosquitto_sub -h localhost -t zigbee2mqtt/bridge/devices -C 1 -W 5'
```
得 119KB JSON，本地 python 解析（不入仓库原始 JSON）。

## 结果
- 协调器 1 + 设备 33（Router 22 / EndDevice 11）。
- 电源：市电 23 / 电池 8 / DC 2。厂商：Tuya 12 / Aqara 11 / ORVIBO 5 / Lilistore 3 / Xiaomi 1 / HOBEIAN 1。
- 类别：开关 8 / 插座 6 / 窗帘 7 / 传感器 7 / 三相电表 3 / 中继 2。
- 4 个 ORVIBO 窗帘 z2m 未完整支持（auto-generated definition）。

## 验证
JSON 条目数与分类自洽（33+1）；友好名均为中文可读。

## 关键发现 / 运维点
- 8 个电池设备需低电量监控 → 纳入未来 `patrol`。
- 单点：z2m 依赖 n100 的 `zigbee2mqtt` + `z2m-mqtt-1`；任一挂全屋 Zigbee 失联。
- 有三相双向电表（Tuya PJ-1203A）——可做家庭用电监控数据源。

## 回滚
纯只读，无需回滚。

## 影响
- 新增 `inventory/iot.md`（Zigbee 设备名册 + 刷新命令）。
- `inventory/services.md`：智能家居段链接到 iot.md。

## 后续
- [ ] 电池电量/在线状态 = 动态事实，未来 patrol 从 z2m 拉。
- [ ] Wi-Fi/其它非 Zigbee IoT（如有）未涵盖；需要时走 HA 设备注册表或网络扫描。
