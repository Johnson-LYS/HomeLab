---
date: 2026-05-30
operator: ai
affected: [jonas]
risk: low
status: success
guardrails: [AUTO]
---

# 只读盘点 QNAP jonas 存储与健康

## 目的
摸清 QNAP 存储布局与那块 16T 唯一盘（RED-01）的健康，提前掌握单点风险。

## 执行
只读（未改动），经 1Password Agent：
```
ssh jonas 'cat /proc/mdstat; df -h; qcli_storage; qcli_storage -d; get_hd_smartinfo -d 1'
```

结果：
- 盘：Port1 /dev/sda 14.55TB **Seagate ST16000NM000J**（Exos）；Port3 /dev/nvme0n1 465.76GB **ZHITAI Ti600 500GB**。
- RAID：md2(sda3) Single `[U]` 在线；md1(nvme) Single。
- 卷：DataVol1 `/share/CACHEDEV2_DATA` 14.3T 用 **77%**（剩 3.3T）；SSD `/share/CACHEDEV1_DATA` 402G 用 24%。
- Emby：`docker` 不存在 → 很可能 QPKG（未确认路径）。

## 验证
- 阵列在线（`[U]`），盘型号确认为企业 Exos。
- df/qcli_storage 双向一致。

## 边界 / 未完成
- 属性级 SMART（`get_hd_smartinfo -d 1`）→ **"Open device fail"**：`Johnson` 非 root，无权读裸盘。
  未提权（不私自 sudo）。重映射扇区/通电时长/温度等未获取。

## 回滚
纯只读，无需回滚。

## 影响
- `inventory/devices.md`：新增「QNAP 存储」段（盘型号/RAID/卷/用量 + 单点风险提示）。
- `inventory/services.md`：QNAP 段更新（Emby 疑 QPKG、存储核实）。

## 后续（重要）
- [ ] 🔴 16T 单盘单点：定备份策略（→ 未来 `backup-verify` skill）。当前 77% 将满。
- [ ] SMART 监控需 root 方案：QNAP GUI / 授权只读命令。
- [ ] 确认 Emby QPKG 安装路径与端口。
- [ ] PVE (.16) 只读盘点。
