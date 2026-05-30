---
last_verified: 2026-05-30
verified_by: ai
source: "ssh n100 → MQTT 保留主题 zigbee2mqtt/bridge/devices（只读订阅）"
status: verified
---

# IoT 设备清单（Zigbee / zigbee2mqtt）

> 绝大多数 IoT 为 Zigbee，经 **zigbee2mqtt（n100，容器 `zigbee2mqtt`）** 接入。
> 本清单为**设备名册**（半稳定）；电量/在线状态是动态事实，不在此固化。
> 刷新：`ssh n100 'docker exec z2m-mqtt-1 mosquitto_sub -h localhost -t zigbee2mqtt/bridge/devices -C 1 -W 5'`

## 概览（2026-05-30）

- 协调器 1 + 设备 **33**（Router 22 / EndDevice 11）
- 电源：市电 23 · 电池 **8** · DC 2
- 厂商：Tuya 12 · Aqara 11 · ORVIBO 5 · Lilistore 3 · Xiaomi 1 · HOBEIAN 1
- ⚠ z2m 未完整支持 4 个（ORVIBO 窗帘，auto-generated definition，控制可能不全）

> Router 类（市电）兼作 Zigbee mesh 中继；EndDevice 多为电池设备。

## 开关 / 面板（8）
| 名称 | 厂商 | 型号 |
|---|---|---|
| 主卧绿米 E1 单控 | Aqara | QBKG38LM |
| 主卧绿米 E1 双控 | Aqara | QBKG39LM |
| 厨房绿米 E1 双控 | Aqara | QBKG39LM |
| 公卫开关 / 公卫走廊开关 | Aqara | ZNQBKG31LM |
| 欧瑞博三控客厅 | ORVIBO | T30W3Z |
| (0xa4c1380990e90098) | HOBEIAN | ZG-301Z |
| 绿米无线双控 🔋 | Aqara | WXKG17LM（无线遥控）|

## 插座 / 电源（6）
| 名称 | 厂商 | 型号 | 备注 |
|---|---|---|---|
| 主位吹风机 / 冰箱 / 洗烘套 | Aqara | QBCZ11LM | 墙面插座 |
| 涂鸦智能插座 / 热水器 | Tuya | TS011F_plug_3 | 带功率计量 |
| 小米插座zigbee | Xiaomi | ZNCZ02LM | |

## 窗帘电机（7）
| 名称 | 厂商 | 型号 | 备注 |
|---|---|---|---|
| 书房纱帘 / 客厅窗帘 / 次卧纱帘 | Lilistore | TS0601_lilistore | |
| 主卧纱帘 / 主卧遮光帘 / 外次卧遮光帘 / 里次卧遮光帘 | ORVIBO | (auto-gen) | ⚠ z2m 未完整支持 |

## 传感器（7，多为电池 🔋）
| 名称 | 厂商 | 型号 | 类型 |
|---|---|---|---|
| 人体传感器厨房 🔋 | Aqara | RTCGQ15LM | 人体移动 |
| 人感公卫 / 人感玄关 🔋 | Tuya | ZG-204ZL | 人体+照度 |
| 入户门 🔋 | Tuya | TS0203 | 门窗磁 |
| 绿米温度湿度气压计 🔋 | Aqara | WSDCGQ11LM | 温湿度气压 |
| 垂丝茉莉 / 绿天鹅绒海芋 🔋 | Tuya | TS0601_soil_3 | 土壤湿度（植物）|

## 计量（3）
| 名称 | 厂商 | 型号 | 备注 |
|---|---|---|---|
| A相 / B相 / C相电表 | Tuya | PJ-1203A | **三相双向电能计量**（80A）|

## 中继（2）
| 名称 | 厂商 | 型号 | 电源 |
|---|---|---|---|
| 中继器 / 中继器主卧 | Tuya | TS0207_repeater | DC |

## 运维要点
- 🔋 **8 个电池设备**需关注低电量（没电即掉线）→ 适合纳入未来 `patrol` 巡检（z2m 暴露各设备 `battery`）。
- ⚠ 4 个 ORVIBO 窗帘 z2m 未完整支持，固件/换型号时注意。
- 数据闸口：z2m 依赖 n100 的 mosquitto（`z2m-mqtt-1`，:1883）+ `zigbee2mqtt` 容器；二者任一挂 → 全屋 Zigbee 失联。
