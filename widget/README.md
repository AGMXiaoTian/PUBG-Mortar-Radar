# 战术雷达终端 — Xbox Game Bar 小组件

Xbox Game Bar 透明叠加小组件，用于在 PUBG 游戏中实时显示迫击炮测距数据和标尺。

## 包含的小组件

| 组件 | 名称 | 功能 |
|------|------|------|
| CalculatorWidget | 迫击炮测距 | 显示 4 个队友颜色标点的实时距离数字 |
| RulerWidget | 迫击炮标尺 | 攻城模式下绘制垂直迫击炮密位标尺 + Panzer 火箭筒准星 |

## 开发环境

- Visual Studio 2022
- .NET 9.0 / UWP
- Windows 10 SDK (19041+)

## 构建与部署

1. 用 Visual Studio 2022 打开 `TacticalRadarFinal.sln`
2. 右键项目 → 发布 → 选择目标架构 (x64/x86/ARM64)
3. 生成 `.msix` 包后双击安装（需开启开发者模式或信任证书）

## 数据协议

小组件每 50ms 从 `ApplicationData.Current.LocalFolder` 读取 `radar_data.json`：

```json
{
  "distances": ["150", "230", "0", "410"],
  "manual_dist": "200",
  "siege": true,
  "panzer_on": false,
  "ruler_data": [
    {"m": 0, "tick": 5, "dial": 650},
    {"m": 1, "tick": 12, "dial": 720}
  ],
  "panzer_data": [
    {"m": 0, "drop": 100, "dist": 150}
  ]
}
```

### 标点颜色映射 (m)

| m | 颜色 |
|---|------|
| 0 | 黄 (Yellow) |
| 1 | 红/橙 (Red-Orange) |
| 2 | 蓝 (Blue) |
| 3 | 绿 (Green) |
| 4 | 白 (手动测距) |

## 注意事项

- `Package.appxmanifest` 中的 `Publisher="CN=Earomanga"` 绑定开发者的临时证书，其他开发者构建时 Visual Studio 会自动生成新的临时密钥
- 小组件需要在 Xbox Game Bar (Win+G) 中手动添加到游戏叠加层
- 该小组件依赖后端 Python 脚本写入 `radar_data.json`，确保后端先启动

## 依赖 (NuGet)

- `Microsoft.Gaming.XboxGameBar` — Xbox Game Bar SDK
- `Microsoft.NETCore.UniversalWindowsPlatform` — UWP 运行时
