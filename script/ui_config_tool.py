import sys
import json
import os
import ctypes
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QGroupBox, QMessageBox, QSpinBox, 
                             QComboBox, QTabWidget, QFormLayout, QSlider, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter, QColor, QPen

# ==========================================
# 核心数据字典
# ==========================================
RES_PRESETS = {
    "4K (3840x2160)": {
        "tiny": {"cx": 3512, "cy": 1836, "x1": 3254, "y1": 1583, "x2": 3774, "y2": 2103, "p100": 129.6},
        "small": {"cx": 3312, "cy": 1636, "x1": 2853, "y1": 1182, "x2": 3840, "y2": 2160, "p100": 129.6},
        "big": {"cx": 1919, "cy": 1076, "x1": 0, "y1": 0, "x2": 3840, "y2": 2160, "p100": 133.0},
        "def_x_tiny": 3200, "def_y_tiny": 1700, "def_x_small": 2800, "def_y_small": 1100,
        "max_w": 3840, "max_h": 2160
    },
    "2K (2560x1440)": {
        "tiny": {"cx": 2342, "cy": 1224, "x1": 2170, "y1": 1055, "x2": 2515, "y2": 1400, "p100": 87.5},
        "small": {"cx": 2208, "cy": 1090, "x1": 1905, "y1": 700, "x2": 2515, "y2": 1440, "p100": 87.5},
        "big": {"cx": 1279, "cy": 716, "x1": 0, "y1": 0, "x2": 2560, "y2": 1440, "p100": 90.0},
        "def_x_tiny": 2190, "def_y_tiny": 1020, "def_x_small": 1920, "def_y_small": 740,
        "max_w": 2560, "max_h": 1440
    },
    "16:10 (2560x1600)": {
        "tiny": {"cx": 2317, "cy": 1360, "x1": 2127, "y1": 1172, "x2": 2513, "y2": 1558, "p100": 96.0},
        "small": {"cx": 2169, "cy": 1211, "x1": 1831, "y1": 876, "x2": 2513, "y2": 1558, "p100": 96.0},
        "big": {"cx": 1279, "cy": 796, "x1": 0, "y1": 0, "x2": 2560, "y2": 1600, "p100": 101.0},
        "def_x_tiny": 2150, "def_y_tiny": 1150, "def_x_small": 1850, "def_y_small": 850,
        "max_w": 2560, "max_h": 1600
    },
    "1080P (1920x1080)": {
        "tiny": {"cx": 1757, "cy": 917, "x1": 1427, "y1": 590, "x2": 1888, "y2": 1052, "p100": 65.8},
        "small": {"cx": 1657, "cy": 817, "x1": 1427, "y1": 590, "x2": 1888, "y2": 1052, "p100": 65.8},
        "big": {"cx": 959, "cy": 536, "x1": 0, "y1": 0, "x2": 1920, "y2": 1080, "p100": 68.0},
        "def_x_tiny": 1700, "def_y_tiny": 950, "def_x_small": 1400, "def_y_small": 550,
        "max_w": 1920, "max_h": 1080
    }
}

COLOR_PRESETS = {
    "默认色彩": {"y": "233,229,17", "r": "218,98,38", "b": "58,160,217", "g": "68,181,73"},
    "绿色盲": {"y": "251,237,33", "r": "219,119,39", "b": "0,98,255", "g": "3,244,164"},
    "红色盲": {"y": "251,237,33", "r": "244,112,22", "b": "40,89,224", "g": "26,198,141"},
    "蓝色盲": {"y": "251,237,33", "r": "241,100,72", "b": "67,120,187", "g": "0,209,203"}
}

# ==========================================
# 极简电竞风渐变样式表
# ==========================================
MODERN_STYLE = """
QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #232526, stop:1 #414345); }
QWidget { color: #E0E0E0; font-family: 'Microsoft YaHei', 'Segoe UI'; }
QWidget#centralWidget { background: transparent; }
QTabWidget::pane { border: 1px solid #444444; border-radius: 8px; background: rgba(30, 30, 35, 0.7); }
QTabBar::tab { background: #3A3A40; color: #AAAAAA; padding: 10px 25px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-weight: bold; font-size: 14px; border: 1px solid #333333; border-bottom: none; margin-right: 2px; }
QTabBar::tab:selected { background: #2C2C32; color: #FF6B00; border-bottom: 2px solid #FF6B00; }
QGroupBox { border: 1px solid #555555; border-radius: 8px; margin-top: 2ex; font-weight: bold; color: #CCCCCC; background: rgba(40, 40, 45, 0.4); }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 15px; color: #FF6B00; }
QComboBox, QSpinBox { background-color: #1A1A1D; border: 1px solid #555555; padding: 6px 10px; border-radius: 4px; color: #FFFFFF; font-weight: bold; }
QComboBox QAbstractItemView { background-color: #1A1A1D; color: #FFFFFF; border: 1px solid #555555; selection-background-color: #FF6B00; outline: none; }
QComboBox::drop-down { border: 0px; }
QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF416C, stop:1 #FF4B2B); color: #FFFFFF; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 15px; border: none; }
QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5B81, stop:1 #FF664A); }
QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E0355A, stop:1 #E03F22); }
QPushButton#resetBtn { background: #555555; font-size: 13px; padding: 8px; }
QPushButton#resetBtn:hover { background: #666666; }
QLabel { font-size: 13px; background: transparent; }
QMessageBox { background-color: #222226; border: 1px solid #444444; }
QMessageBox QLabel { color: #E0E0E0; font-size: 13px; }
QMessageBox QPushButton { min-width: 80px; padding: 6px 15px; font-size: 13px; }
QSlider::groove:horizontal { border: 1px solid #333; height: 6px; background: #1A1A1D; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #FF6B00; border-radius: 3px; }
QSlider::handle:horizontal { background: #FFFFFF; border: 1px solid #777; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }
QSlider::handle:horizontal:hover { background: #FF6B00; border: 1px solid #FFFFFF; }
QCheckBox { font-size: 14px; font-weight: bold; color: #4FD1C5; }
QCheckBox::indicator { width: 18px; height: 18px; border: 2px solid #555; border-radius: 4px; background: #1A1A1D; }
QCheckBox::indicator:checked { background: #4FD1C5; border: 2px solid #4FD1C5; }
"""

# ==========================================
# 物理全屏透明靶场
# ==========================================
class HologramTarget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.font_size = 22
        self.tx = 0; self.ty = 0; self.sx = 0; self.sy = 0
        self.is_active = False

    def toggle_active(self, state):
        self.is_active = state
        if state:
            self.setGeometry(QApplication.primaryScreen().geometry())
            self.show()
            self.make_click_through()
        else:
            self.hide()

    def make_click_through(self):
        hwnd = int(self.winId())
        user32 = ctypes.windll.user32
        ex_style = user32.GetWindowLongW(hwnd, -20)
        user32.SetWindowLongW(hwnd, -20, ex_style | 0x00080000 | 0x00000020)

    def update_data(self, font, tx, ty, sx, sy):
        self.font_size = font
        self.tx = tx; self.ty = ty; self.sx = sx; self.sy = sy
        if self.is_active: self.update()

    def paintEvent(self, event):
        if not self.is_active: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setFont(QFont("微软雅黑", self.font_size, QFont.Weight.Bold))
        painter.setPen(QColor("#FF6B00"))
        painter.drawText(self.tx, self.ty, "[385] (小小图预览)")
        painter.setPen(QColor("#4FD1C5"))
        painter.drawText(self.sx, self.sy, "[820] (大地图预览)")

# ==========================================
# 主控制台
# ==========================================
class ConfigToolPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PUBG 迫击炮雷达配置系统 V1.0')
        self.resize(680, 750) # 稍微加长以适应新的输入框
        self.setStyleSheet(MODERN_STYLE)
        
        self.hologram = HologramTarget()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.initUI()
        self.load_existing_config()
        self.bind_signals()
        self.update_live_preview()

    def initUI(self):
        header = QLabel("TACTICAL FIRE CONTROL SYSTEM")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #FF6B00; margin-bottom: 10px; letter-spacing: 2px;")
        self.main_layout.addWidget(header)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # --- Tab 1: 核心引擎设置 ---
        self.tab_engine = QWidget()
        layout_engine = QVBoxLayout(self.tab_engine)
        
        group_visual = QGroupBox("屏幕视觉捕捉参数")
        form_visual = QFormLayout(group_visual)
        form_visual.setSpacing(20)
        
        self.combo_res = QComboBox()
        self.combo_res.addItems(list(RES_PRESETS.keys()))
        self.combo_color = QComboBox()
        self.combo_color.addItems(list(COLOR_PRESETS.keys()))
        self.spin_tolerance = QSpinBox()
        self.spin_tolerance.setRange(1, 30)
        self.spin_tolerance.setSuffix(" (建议10-15)")
        
        form_visual.addRow("游戏分辨率设置:", self.combo_res)
        form_visual.addRow("色盲模式预设:", self.combo_color)
        form_visual.addRow("颜色识别容差:", self.spin_tolerance)
        
        layout_engine.addWidget(group_visual)
        layout_engine.addStretch()
        self.tabs.addTab(self.tab_engine, "视觉参数")

        # --- Tab 2: HUD 位置与靶场 ---
        self.tab_ui = QWidget()
        layout_ui = QVBoxLayout(self.tab_ui)

        self.check_preview = QCheckBox("开启物理全屏透明预览靶场 (进游戏校对必备)")
        layout_ui.addWidget(self.check_preview)

        group_pos = QGroupBox("文字悬浮坐标 (支持拖拽滑块或输入数字)")
        form_pos = QFormLayout(group_pos)
        form_pos.setSpacing(12)

        self.spin_font, self.slider_font = self.create_slider_row(10, 80)
        form_pos.addRow("字号大小:", self.slider_font)
        
        lbl_tiny = QLabel("--- 小小图距离显示坐标 ---")
        lbl_tiny.setStyleSheet("color: #FF6B00; font-weight: bold; margin-top: 5px;")
        form_pos.addRow(lbl_tiny)
        self.spin_tiny_x, self.slider_tiny_x = self.create_slider_row(0, 5000)
        form_pos.addRow("X 坐标:", self.slider_tiny_x)
        self.spin_tiny_y, self.slider_tiny_y = self.create_slider_row(0, 3000)
        form_pos.addRow("Y 坐标:", self.slider_tiny_y)
        
        lbl_small = QLabel("--- 大地图距离显示坐标 ---")
        lbl_small.setStyleSheet("color: #4FD1C5; font-weight: bold; margin-top: 5px;")
        form_pos.addRow(lbl_small)
        self.spin_small_x, self.slider_small_x = self.create_slider_row(0, 5000)
        form_pos.addRow("X 坐标:", self.slider_small_x)
        self.spin_small_y, self.slider_small_y = self.create_slider_row(0, 3000)
        form_pos.addRow("Y 坐标:", self.slider_small_y)

        layout_ui.addWidget(group_pos)
        
        btn_reset_pos = QPushButton("一键重置文字坐标为当前分辨率默认值")
        btn_reset_pos.setObjectName("resetBtn")
        btn_reset_pos.clicked.connect(self.reset_text_positions)
        layout_ui.addWidget(btn_reset_pos)
        layout_ui.addStretch()
        
        self.tabs.addTab(self.tab_ui, "文字位置")

        # --- Tab 3: 识别区域与性能控制 (包含中心锚点) ---
        self.tab_perf = QWidget()
        layout_perf = QVBoxLayout(self.tab_perf)

        group_perf = QGroupBox("底层扫描性能")
        form_perf = QFormLayout(group_perf)
        self.spin_fps, self.slider_fps = self.create_slider_row(1, 60)
        form_perf.addRow("扫描频率 (FPS):", self.slider_fps)
        layout_perf.addWidget(group_perf)

        group_rect = QGroupBox("图像识别区域绝对坐标 (如果缩放比例特殊可修改)")
        layout_rect = QVBoxLayout(group_rect)
        layout_rect.setSpacing(10)
        
        lbl_info = QLabel("物理学中心锚点：自身白箭头中心像素点的绝对坐标。算法以此为原点测距。")
        lbl_info.setStyleSheet("color: #888888; font-size: 12px; margin-bottom: 5px;")
        layout_rect.addWidget(lbl_info)

        lbl_rect_tiny = QLabel("--- 小小图扫描区域与中心点 ---")
        lbl_rect_tiny.setStyleSheet("color: #FF6B00; font-weight: bold;")
        layout_rect.addWidget(lbl_rect_tiny)
        self.wg_t_rect, self.sp_t_x1, self.sp_t_y1, self.sp_t_x2, self.sp_t_y2 = self.create_rect_input_row()
        self.wg_t_center, self.sp_t_cx, self.sp_t_cy = self.create_center_input_row()
        layout_rect.addWidget(self.wg_t_rect)
        layout_rect.addWidget(self.wg_t_center)

        lbl_rect_small = QLabel("--- 小地图扫描区域与中心点 ---")
        lbl_rect_small.setStyleSheet("color: #4FD1C5; font-weight: bold; margin-top: 5px;")
        layout_rect.addWidget(lbl_rect_small)
        self.wg_s_rect, self.sp_s_x1, self.sp_s_y1, self.sp_s_x2, self.sp_s_y2 = self.create_rect_input_row()
        self.wg_s_center, self.sp_s_cx, self.sp_s_cy = self.create_center_input_row()
        layout_rect.addWidget(self.wg_s_rect)
        layout_rect.addWidget(self.wg_s_center)
        
        btn_reset_rect = QPushButton("一键重置识别区域为当前分辨率默认值")
        btn_reset_rect.setObjectName("resetBtn")
        btn_reset_rect.clicked.connect(self.reset_rect_positions)
        layout_rect.addWidget(btn_reset_rect)

        layout_perf.addWidget(group_rect)
        layout_perf.addStretch()
        self.tabs.addTab(self.tab_perf, "识别引擎")

        # --- 底部保存按钮 ---
        self.btn_save = QPushButton("覆写 Config.json 配置并生效")
        self.btn_save.clicked.connect(self.save_config)
        self.main_layout.addWidget(self.btn_save)

    def create_slider_row(self, min_val, max_val):
        h_layout = QHBoxLayout()
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setFixedWidth(75)
        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)
        h_layout.addWidget(slider)
        h_layout.addWidget(spin)
        return spin, h_layout

    def create_rect_input_row(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        sp_x1 = QSpinBox(); sp_x1.setRange(0, 5000); sp_x1.setPrefix("左上 X: ")
        sp_y1 = QSpinBox(); sp_y1.setRange(0, 5000); sp_y1.setPrefix("左上 Y: ")
        sp_x2 = QSpinBox(); sp_x2.setRange(0, 5000); sp_x2.setPrefix("右下 X: ")
        sp_y2 = QSpinBox(); sp_y2.setRange(0, 5000); sp_y2.setPrefix("右下 Y: ")

        for sp in [sp_x1, sp_y1, sp_x2, sp_y2]:
            sp.setFixedWidth(150)

        layout.addWidget(sp_x1)
        layout.addWidget(sp_y1)
        lbl_arrow = QLabel("   ")
        lbl_arrow.setFixedWidth(15)
        layout.addWidget(lbl_arrow)
        layout.addWidget(sp_x2)
        layout.addWidget(sp_y2)
        layout.addStretch()

        return widget, sp_x1, sp_y1, sp_x2, sp_y2

    def create_center_input_row(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        sp_cx = QSpinBox(); sp_cx.setRange(0, 5000); sp_cx.setPrefix("玩家中心 X: ")
        sp_cy = QSpinBox(); sp_cy.setRange(0, 5000); sp_cy.setPrefix("玩家中心 Y: ")
        
        sp_cx.setFixedWidth(180)
        sp_cy.setFixedWidth(180)

        layout.addWidget(sp_cx)
        layout.addWidget(sp_cy)
        layout.addStretch()
        return widget, sp_cx, sp_cy

    def load_existing_config(self):
        if not os.path.exists("config.json"):
            self.update_slider_ranges()
            self.reset_text_positions()
            self.reset_rect_positions()
            self.spin_fps.setValue(10)
            return

        try:
            with open("config.json", "r", encoding="utf-8") as f:
                old_conf = json.load(f)
            
            if "resolution" in old_conf: self.combo_res.setCurrentText(old_conf["resolution"])
            if "color_preset" in old_conf: self.combo_color.setCurrentText(old_conf["color_preset"])
            if "color_tolerance" in old_conf: self.spin_tolerance.setValue(old_conf["color_tolerance"])
            
            self.update_slider_ranges()

            if "ui_font_size" in old_conf: self.spin_font.setValue(old_conf["ui_font_size"])
            if "ui_pos_tiny" in old_conf:
                parts = old_conf["ui_pos_tiny"].strip('+').split('+')
                if len(parts) == 2:
                    self.spin_tiny_x.setValue(int(parts[0])); self.spin_tiny_y.setValue(int(parts[1]))
            if "ui_pos_small" in old_conf:
                parts = old_conf["ui_pos_small"].strip('+').split('+')
                if len(parts) == 2:
                    self.spin_small_x.setValue(int(parts[0])); self.spin_small_y.setValue(int(parts[1]))
            
            if "scan_fps" in old_conf: self.spin_fps.setValue(old_conf["scan_fps"])
            
            # 恢复截取区域与中心点
            if "monitor_tiny" in old_conf and "player_tiny" in old_conf:
                m_tiny = old_conf["monitor_tiny"]
                p_tiny = old_conf["player_tiny"]
                self.sp_t_x1.setValue(m_tiny["left"])
                self.sp_t_y1.setValue(m_tiny["top"])
                self.sp_t_x2.setValue(m_tiny["left"] + m_tiny["width"])
                self.sp_t_y2.setValue(m_tiny["top"] + m_tiny["height"])
                # 反推绝对坐标中心点
                self.sp_t_cx.setValue(m_tiny["left"] + p_tiny["x"])
                self.sp_t_cy.setValue(m_tiny["top"] + p_tiny["y"])
            else:
                self.reset_rect_positions()

            if "monitor_small" in old_conf and "player_small" in old_conf:
                m_small = old_conf["monitor_small"]
                p_small = old_conf["player_small"]
                self.sp_s_x1.setValue(m_small["left"])
                self.sp_s_y1.setValue(m_small["top"])
                self.sp_s_x2.setValue(m_small["left"] + m_small["width"])
                self.sp_s_y2.setValue(m_small["top"] + m_small["height"])
                self.sp_s_cx.setValue(m_small["left"] + p_small["x"])
                self.sp_s_cy.setValue(m_small["top"] + p_small["y"])

        except Exception as e:
            print("读取配置异常，已恢复预设。")
            self.update_slider_ranges()
            self.reset_text_positions()
            self.reset_rect_positions()

    def bind_signals(self):
        self.combo_res.currentTextChanged.connect(self.on_resolution_changed)
        self.check_preview.stateChanged.connect(self.toggle_hologram)
        controls = [self.spin_font, self.spin_tiny_x, self.spin_tiny_y, self.spin_small_x, self.spin_small_y]
        for control in controls:
            control.valueChanged.connect(self.update_live_preview)

    def on_resolution_changed(self):
        self.update_slider_ranges()
        self.reset_text_positions()
        self.reset_rect_positions()

    def toggle_hologram(self, state):
        self.hologram.toggle_active(state == Qt.CheckState.Checked.value)
        self.update_live_preview()

    def update_slider_ranges(self):
        res_key = self.combo_res.currentText()
        preset = RES_PRESETS[res_key]
        self.spin_tiny_x.setMaximum(preset["max_w"])
        self.spin_small_x.setMaximum(preset["max_w"])
        self.spin_tiny_y.setMaximum(preset["max_h"])
        self.spin_small_y.setMaximum(preset["max_h"])

    def update_live_preview(self):
        self.hologram.update_data(
            font=self.spin_font.value(),
            tx=self.spin_tiny_x.value(), ty=self.spin_tiny_y.value(),
            sx=self.spin_small_x.value(), sy=self.spin_small_y.value()
        )

    def reset_text_positions(self):
        res_key = self.combo_res.currentText()
        preset = RES_PRESETS[res_key]
        self.spin_tiny_x.setValue(preset["def_x_tiny"])
        self.spin_tiny_y.setValue(preset["def_y_tiny"])
        self.spin_small_x.setValue(preset["def_x_small"])
        self.spin_small_y.setValue(preset["def_y_small"])
        self.update_live_preview()

    def reset_rect_positions(self):
        res_key = self.combo_res.currentText()
        preset = RES_PRESETS[res_key]
        
        self.sp_t_x1.setValue(preset["tiny"]["x1"])
        self.sp_t_y1.setValue(preset["tiny"]["y1"])
        self.sp_t_x2.setValue(preset["tiny"]["x2"])
        self.sp_t_y2.setValue(preset["tiny"]["y2"])
        self.sp_t_cx.setValue(preset["tiny"]["cx"])
        self.sp_t_cy.setValue(preset["tiny"]["cy"])

        self.sp_s_x1.setValue(preset["small"]["x1"])
        self.sp_s_y1.setValue(preset["small"]["y1"])
        self.sp_s_x2.setValue(preset["small"]["x2"])
        self.sp_s_y2.setValue(preset["small"]["y2"])
        self.sp_s_cx.setValue(preset["small"]["cx"])
        self.sp_s_cy.setValue(preset["small"]["cy"])

    def convert_rgb_to_bgr_bounds(self, rgb_str, tolerance):
        r, g, b = map(int, rgb_str.split(','))
        lower = [max(0, b - tolerance), max(0, g - tolerance), max(0, r - tolerance)]
        upper = [min(255, b + tolerance), min(255, g + tolerance), min(255, r + tolerance)]
        return lower, upper

    def save_config(self):
        res_key = self.combo_res.currentText()
        res_data = RES_PRESETS[res_key]
        color_data = COLOR_PRESETS[self.combo_color.currentText()]
        tolerance = self.spin_tolerance.value()

        def build_map_data(x1, y1, x2, y2, cx, cy, orig_data):
            width = x2 - x1
            height = y2 - y1
            if width <= 0 or height <= 0:
                width = orig_data["x2"] - orig_data["x1"]
                height = orig_data["y2"] - orig_data["y1"]
            
            # 计算绝对坐标系下，玩家中心点在截图区域内的相对坐标
            rel_cx = cx - x1
            rel_cy = cy - y1
            
            multiplier = 100.0 / orig_data["p100"]
            
            return {"top": y1, "left": x1, "width": width, "height": height}, {"x": rel_cx, "y": rel_cy}, multiplier

        # 生成包含了用户自定义锚点的底层数据
        monitor_tiny, player_tiny, mult_tiny = build_map_data(
            self.sp_t_x1.value(), self.sp_t_y1.value(), self.sp_t_x2.value(), self.sp_t_y2.value(), self.sp_t_cx.value(), self.sp_t_cy.value(), res_data["tiny"]
        )
        monitor_small, player_small, mult_small = build_map_data(
            self.sp_s_x1.value(), self.sp_s_y1.value(), self.sp_s_x2.value(), self.sp_s_y2.value(), self.sp_s_cx.value(), self.sp_s_cy.value(), res_data["small"]
        )
        
        # 大地图不开放中心点输入，走默认解析
        monitor_big, player_big, mult_big = build_map_data(
            res_data["big"]["x1"], res_data["big"]["y1"], res_data["big"]["x2"], res_data["big"]["y2"], res_data["big"]["cx"], res_data["big"]["cy"], res_data["big"]
        ) 

        markers = []
        color_map = [("P1(黄)", color_data["y"], "#FFFF00"), 
                     ("P2(红/橙)", color_data["r"], "#FF5500"),
                     ("P3(蓝)", color_data["b"], "#3399FF"), 
                     ("P4(绿)", color_data["g"], "#33FF33")]
        for name, rgb_str, hex_code in color_map:
            lower, upper = self.convert_rgb_to_bgr_bounds(rgb_str, tolerance)
            markers.append({"name": name, "color_hex": hex_code, "lower_bgr": lower, "upper_bgr": upper})

        pos_tiny = f"+{self.spin_tiny_x.value()}+{self.spin_tiny_y.value()}"
        pos_small = f"+{self.spin_small_x.value()}+{self.spin_small_y.value()}"

        final_config = {
            "resolution": res_key,
            "color_preset": self.combo_color.currentText(),
            "color_tolerance": tolerance,            
            "monitor_tiny": monitor_tiny, "player_tiny": player_tiny, "multiplier_tiny": mult_tiny,
            "monitor_small": monitor_small, "player_small": player_small, "multiplier_small": mult_small,
            "monitor_big": monitor_big, "player_big": player_big, "multiplier_big": mult_big,
            "ui_pos_tiny": pos_tiny, 
            "ui_pos_small": pos_small,
            "ui_font_size": self.spin_font.value(),
            "scan_fps": self.spin_fps.value(),
            "markers": markers
        }

        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(final_config, f, indent=4)
            
        QMessageBox.information(self, "部署成功", "战术配置已全面生成。\n包含自定义坐标和中心物理锚点。\n请重启主程序以应用更改。")

    def closeEvent(self, event):
        self.hologram.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ConfigToolPro()
    ex.show()
    sys.exit(app.exec())