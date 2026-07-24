---
date: 2026-07-24
operator: ai
affected: [homeassistant, repository]
risk: low
status: success
guardrails: []
---

# 迁入 Home Assistant 户型灯光配置源码

## 目的

将本地香山府户型灯光演练项目纳入 HomeLab 仓库，统一保存可部署配置、图片资源、安装说明和本地演练页。

## 执行

新增目录：

```text
scripts/home-assistant-floorplan/
```

迁入并整理：

- Home Assistant Lovelace YAML Dashboard。
- 9 个多灯房间的灯光组配置模板。
- 玄关、阳台两个单灯控制模板。
- 12 张英文文件名的户型图层。
- 使用同一套生产图片资源的本地 HTML 演练页。
- 独立 Dashboard 与合并进现有 Dashboard 两种部署说明。

未迁入生成的 ZIP、重复的中文文件名原图、`.DS_Store` 或任何凭证。

## 验证

- 仓库迁移前工作区为干净状态。
- 3 个 YAML 文件均可解析。
- Dashboard 包含 9 个灯光组控制、9 个 Subview、2 个单灯和 5 个 `screen` 混合图层。
- 12 个图片引用与实际资源文件一一对应。
- 未发现密码、token、API key、Bearer 值或 `op://` 以外的凭证内容。

## 回滚

本次只增加仓库文件，未修改运行中的 Home Assistant。回滚时移除本次新增目录与本日志即可；不涉及设备、容器、数据库或 HA 配置回滚。

## 影响

- 新增 Home Assistant 户型灯光配置源码。
- 未部署到 n100，未修改 Home Assistant 服务状态。
- 因运行环境事实未变化，本次不更新 `inventory/`。

## 后续

- [ ] 收集 9 个房间的真实灯具实体 ID，以及玄关、阳台单灯实体 ID。
- [ ] 在人工确认后备份并部署到 Home Assistant。
- [ ] 部署成功后更新 `inventory/services.md` 并追加实际部署记录。
