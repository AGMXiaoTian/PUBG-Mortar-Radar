# PUBG Mortar Radar — 迫击炮战术雷达系统

PUBG 迫击炮自动测距与标尺系统。通过屏幕颜色识别 + 弹道物理计算，为 PUBG 中的迫击炮提供实时开火密位。

**安全声明**：本程序为纯外部视觉辅助工具。仅通过屏幕截图进行像素颜色匹配，**不读取游戏内存，不修改任何游戏文件**。

---

## 项目结构

```
PUBG-Mortar-Radar/
├── script/              ← Python 后端：屏幕识别 + 弹道计算
├── widget/              ← Xbox Game Bar 小组件：游戏内透明叠加显示
└── README.md
```

## 工作原理

```
┌─────────────────────────────────┐
│  script/ (Python 后端)           │
│                                 │
│  截取小地图 → OpenCV 颜色识别    │
│      ↓                          │
│  像素坐标 → 真实距离 (米)        │
│      ↓                          │
│  弹道物理计算 → 密位/标尺数据   │
│      ↓                          │
│  写入 radar_data.json           │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  widget/ (Xbox Game Bar 小组件) │
│                                 │
│  Win+G 呼出 → 透明叠加层        │
│  • 距离显示 (黄/红/蓝/绿)       │
│  • 迫击炮密位标尺               │
│  • Panzer 火箭筒准星            │
└─────────────────────────────────┘
```

## 快速开始

### 1. 后端脚本 (script/)

```bash
cd script
pip install -r requirements.txt
cp config.example.json config.json   # 编辑填入你的屏幕坐标
python radar_scanner.py
```

详细说明见 [script/README.md](script/README.md)

### 2. Xbox 小组件 (widget/)

使用 Visual Studio 2022 打开 `widget/TacticalRadarFinal.sln`，编译并部署。

详细说明见 [widget/README.md](widget/README.md)

---

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| F8 | 开启/关闭攻城模式（迫击炮标尺） |
| F9 | 大地图宏指令测距 |
| N | 切换小地图/小小图识别模式 |
| Shift+N | 仅切换游戏地图，不切换脚本模式 |

## 系统要求

- Windows 10/11 (Xbox Game Bar 支持)
- Python 3.10+
- 游戏设置：无边框窗口模式

## 开源协议

本项目仅供学习交流使用。请遵守游戏服务条款。
