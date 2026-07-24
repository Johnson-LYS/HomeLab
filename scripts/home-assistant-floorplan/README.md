# Home Assistant · 香山府户型灯光面板

> 状态：配置源码已入库，**尚未部署到运行中的 Home Assistant**。
> 本目录不包含凭证；所有灯具实体均为待替换的示例 ID。

## 目录

```text
scripts/home-assistant-floorplan/
├── README.md
├── configuration-snippet.yaml
├── light-groups-snippet.yaml
├── floorplan-dashboard.yaml
├── demo/
│   └── index.html
└── www/
    └── floorplan/
        └── 12 张 PNG 图层
```

| 文件 | 用途 | 部署目标 |
|---|---|---|
| `www/floorplan/` | 底图、普通透明亮灯图层、线性减淡光照图层 | `/config/www/floorplan/` |
| `floorplan-dashboard.yaml` | 户型主页面、全开/全关、9 个房间 Subview | `/config/floorplan-dashboard.yaml` |
| `light-groups-snippet.yaml` | 9 个多灯房间的灯光组模板 | 合并进 `/config/configuration.yaml` |
| `configuration-snippet.yaml` | 注册独立 Lovelace YAML Dashboard | 仅独立 Dashboard 方案合并进 `/config/configuration.yaml` |
| `demo/index.html` | 不连接 HA 的本地交互演练页 | 不部署；仅本地预览 |

## 控制模型

| 区域 | 实体模型 | 单击 | 长按 |
|---|---|---|---|
| 玄关、阳台 | 单灯 | 切换单灯 | 更多信息 |
| 其余 9 个区域 | `all: false` 灯光组 | 任意灯开时全部关闭；全关时全部打开 | 进入单灯 Subview |

灯光组 `all: false` 表示任意成员为 `on` 时组状态就是 `on`。户型亮灯图层绑定组实体，因此任一成员灯开启都会点亮整个房间。

## 部署前必须完成

1. 在 `light-groups-snippet.yaml` 中，把每个组的 `entities:` 改成真实单灯实体。
2. 在 `floorplan-dashboard.yaml` 中，把 `light.entry` 和 `light.balcony` 全部替换成真实单灯实体。
3. 同步修改文件末尾 9 个 Subview 中的 Tile，使其与灯光组成员一致。
4. 检查生成的 9 个组实体是否与 Dashboard 预期一致：

| 区域 | Dashboard 预期组实体 |
|---|---|
| 主卧 | `light.master_bedroom` |
| 主卫 | `light.master_bathroom` |
| 厨房 | `light.kitchen` |
| 次卫 | `light.second_bathroom` |
| 次卧 | `light.second_bedroom` |
| 书房 | `light.study` |
| 客厅 | `light.living_room` |
| 餐厅 | `light.dining_room` |
| 洗手台 | `light.washstand` |

如果 HA 因实体名冲突生成 `_2` 等后缀，在 HA 中重命名组实体，或在 Dashboard YAML 中全部替换为实际 ID。

## 部署方式 A：独立 Dashboard

### 文件放置

```text
仓库                                           Home Assistant
scripts/home-assistant-floorplan/www/floorplan → /config/www/floorplan
scripts/home-assistant-floorplan/floorplan-dashboard.yaml
                                               → /config/floorplan-dashboard.yaml
```

### 合并配置

将修改后的 `light-groups-snippet.yaml` 合并进 `/config/configuration.yaml`。如果已有顶级 `light:`，只追加 9 个 `- platform: group` 项，不能创建第二个同级 `light:`。

再将 `configuration-snippet.yaml` 合并进 `/config/configuration.yaml`。如果已有顶级 `lovelace:` 或 `lovelace.dashboards:`，只追加 `xiangshan-floorplan:`，不能创建重复顶级键。

此方式下，`floorplan-dashboard.yaml` 中的 `/xiangshan-floorplan/...` 导航路径可保持不变。

## 部署方式 B：加入现有 Dashboard

1. 图片仍复制到 `/config/www/floorplan/`。
2. 灯光组仍合并到 `/config/configuration.yaml`。
3. 在目标 Dashboard 的原始配置编辑器中备份现有 YAML。
4. 将 `floorplan-dashboard.yaml` 的第一个 View 追加到现有 `views:`；若只要卡片，则仅复制其中 `type: vertical-stack` 开始的完整卡片到目标 View 的 `cards:`。
5. 将文件末尾 9 个 `subview: true` View 追加到现有 Dashboard 的 `views:`。
6. 将所有 `/xiangshan-floorplan/` 替换为现有 Dashboard 的 URL 前缀。
7. 如果户型页的 `path` 改为 `floorplan`，所有 Subview 的 `back_path` 也要返回该路径。

例如现有 Dashboard 地址为 `/lovelace-mobile/home`：

```yaml
navigation_path: /lovelace-mobile/living-room
back_path: /lovelace-mobile/floorplan
```

此方式不使用 `configuration-snippet.yaml`，也不注册新 Dashboard。

## 图片与混合模式

- 普通房间 PNG 使用透明通道直接覆盖。
- 客厅、餐厅、玄关、阳台、洗手台为黑底光照贡献图，必须保留：

```yaml
mix-blend-mode: screen
```

- `/config/www/` 在 HA 前端映射为 `/local/`。部署后先验证：

```text
http://<HA 地址>:8123/local/floorplan/base.png
```

## 验证清单

1. 运行 HA 配置检查，确认 YAML 有效。
2. 重启 HA 后，在开发者工具中确认 9 个灯光组存在。
3. 每个组只打开一盏成员灯，确认组状态为 `on`。
4. 打开户型页，确认对应亮灯图层出现。
5. 单击多灯房间，确认所有成员关闭。
6. 全关状态下再次单击，确认所有成员打开。
7. 长按多灯房间，确认进入正确 Subview。
8. 验证玄关、阳台单灯和全屋总开/总关。
9. 同时打开客厅、餐厅等交叉区域，确认没有黑色遮罩。

## 本地演练

从仓库根目录启动静态服务器：

```bash
python3 -m http.server 8765 --directory scripts/home-assistant-floorplan
```

打开：

```text
http://127.0.0.1:8765/demo/
```

演练页只模拟交互，不读取或控制 HA 实体。

## 安全与运维

- 本目录不得加入 HA token、密码、Cookie、外部访问密钥或包含真实凭证的导出文件。
- 实际部署属于修改 Home Assistant 配置，按 `policies/guardrails.md` 需要人工确认。
- 部署前先备份运行中的 `/config/configuration.yaml` 与目标 Dashboard 配置。
- 实际部署完成后，同一次提交更新 `inventory/services.md` 的核实来源，并向 `operations/log/` 追加部署记录。
