# PUBG 迫击炮标点测距工具
# 单文件自包含版本 — 屏幕识别 + 弹道计算 + 全息标尺叠加
import mss
import numpy as np
import cv2
import time
import math
import keyboard
import threading
import tkinter as tk
import json
import os
import sys
import ctypes
from pynput.keyboard import Controller as KeyboardController, Key

# ==========================================
# 物理参数 (云端变量已内置)
# ==========================================
MORTAR_V = 82.9      # 迫击炮初速 (m/s)  ← 原云端变量 mortarv
MORTAR_G = 9.8       # 重力加速度 (m/s²) ← 原云端变量 mortarg
# coreratio = 1.0    # 距离修正系数，已直接使用 config.json 中的 multiplier

# ==========================================
# 配置与数据加载
# ==========================================
CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("错误: 找不到 config.json。请先运行 '调试工具' 生成配置！")
        sys.exit()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()
UI_FONT_SIZE = config.get("ui_font_size", 22)

# 全局状态变量
is_expanded = False
is_macro_running = False
is_siege_mode = False
current_distances = ["0", "0", "0", "0"]

kb = KeyboardController()
MOUSEEVENTF_WHEEL = 0x0800

def precision_scroll(delta):
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, int(delta), 0)

# ==========================================
# 物理学弹道核心解算引擎
# ==========================================
KEDU_TO_ANGLE = [0, 0.56, 1.69, 2.82, 3.94, 5.06, 6.18, 7.29, 8.40, 9.50, 10.59,
                 11.67, 12.75, 13.82, 14.88, 15.92, 16.96, 17.99, 19.00, 20.00,
                 20.99, 21.97, 22.93, 23.88, 24.82, 25.74]

def get_view_angle(tick):
    abs_tick = abs(tick)
    if abs_tick < len(KEDU_TO_ANGLE):
        return KEDU_TO_ANGLE[abs_tick]
    else:
        return KEDU_TO_ANGLE[-1] + (abs_tick - 25) * 0.92

def calculate_mortar_dial(horizontal_dist, kedu_tick):
    """迫击炮密位计算 — 基于抛物线弹道模型"""
    try:
        dis = float(horizontal_dist)
        if dis <= 0:
            return 0

        view_angle = get_view_angle(kedu_tick)
        if view_angle == 0:
            return int(round(dis))

        height = dis * math.tan(math.radians(view_angle))
        if kedu_tick < 0:
            height = -height

        V = MORTAR_V
        G = MORTAR_G

        a = -G * dis / (2 * V * V)
        c = a - (height / dis)
        delta = 1 - 4 * a * c

        if delta < 0:
            return -1

        sita = (-1 - math.sqrt(delta)) / (2 * a)
        hudu = math.atan(sita)
        dial_dis = (V * V * math.cos(hudu) * math.sin(hudu)) / 4.9
        return int(round(dial_dis))
    except Exception:
        return 0

# ==========================================
# 热键与宏逻辑
# ==========================================
def toggle_map_mode(e):
    global is_expanded
    if keyboard.is_pressed('shift'):
        return
    is_expanded = not is_expanded

def toggle_siege_mode(e):
    global is_siege_mode
    is_siege_mode = not is_siege_mode
    print(f"攻城模式 {'开启' if is_siege_mode else '关闭'}")

def macro_big_map(e):
    global is_macro_running, current_distances
    if is_macro_running:
        return
    is_macro_running = True
    print("大地图测距")

    kb.tap('m')
    kb.tap(Key.space)
    time.sleep(0.1)

    for _ in range(4):
        precision_scroll(120)
        time.sleep(0.03)

    for _ in range(2):
        precision_scroll(-120)
        time.sleep(0.03)

    precision_scroll(40)
    time.sleep(0.3)
    kb.tap(Key.space)
    time.sleep(0.3)

    markers_ranges = []
    for m in config["markers"]:
        markers_ranges.append((np.array(m["lower_bgr"], dtype=np.uint8), np.array(m["upper_bgr"], dtype=np.uint8)))

    with mss.mss() as sct:
        monitor_big = config["monitor_big"]
        player_x = config["player_big"]["x"]
        player_y = config["player_big"]["y"]
        multiplier = config["multiplier_big"]
        screenshot = np.array(sct.grab(monitor_big))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        temp_distances = ["0", "0", "0", "0"]

        for i, (lower, upper) in enumerate(markers_ranges):
            mask = cv2.inRange(frame, lower, upper)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            valid_contours = []
            for c in contours:
                if cv2.contourArea(c) < 5:
                    continue
                x, y, w, h = cv2.boundingRect(c)
                cx, cy = x + w // 2, y + h // 2
                center_dist = math.sqrt((cx - player_x)**2 + (cy - player_y)**2)
                if center_dist < 20 and w < 30 and h < 30:
                    continue
                valid_contours.append(c)

            if valid_contours:
                c = max(valid_contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(c)
                bottom_point = tuple(c[c[:, :, 1].argmax()][0])
                tip_x, tip_y = bottom_point
                if tip_y >= monitor_big["height"] - 3:
                    ping_x, ping_y = x + w // 2, y + h // 2
                else:
                    ping_x, ping_y = tip_x, tip_y

                pixel_dist = math.sqrt((ping_x - player_x)**2 + (ping_y - player_y)**2)
                temp_distances[i] = str(max(0, round(pixel_dist * multiplier)))

        current_distances = temp_distances
        print(f"大地图测距完成: {current_distances}")

    kb.tap('m')
    def release_macro_lock():
        global is_macro_running
        is_macro_running = False
    threading.Timer(5.0, release_macro_lock).start()

# ==========================================
# UI 渲染与全息阵列绑定
# ==========================================
def create_overlay():
    global root, labels_text
    root = tk.Tk()
    root.title("PUBG_Overlay")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-transparentcolor", "black")
    root.config(bg="black")
    root.geometry(config["ui_pos_tiny"])

    # 顶部基础距离显示
    labels_text = []
    for marker in config["markers"]:
        var = tk.StringVar()
        var.set("0")
        labels_text.append(var)
        lbl = tk.Label(root, textvariable=var, font=("微软雅黑", UI_FONT_SIZE, "bold"), fg=marker["color_hex"], bg="black")
        lbl.pack(side=tk.LEFT, padx=12)

    # 攻顶标尺全屏遮罩
    siege_win = tk.Toplevel(root)
    siege_win.attributes('-fullscreen', True)
    siege_win.attributes('-topmost', True)
    siege_win.attributes('-transparentcolor', 'black')
    siege_win.config(bg='black')
    siege_win.withdraw()

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    cx, cy = screen_w // 2, screen_h // 2

    canvas = tk.Canvas(siege_win, bg='black', highlightthickness=0)
    canvas.pack(fill='both', expand=True)

    # 画垂直主轴线
    canvas.create_line(cx, cy - 720, cx, cy + 720, fill="#FF4500", width=1, dash=(2, 4))

    # 全息数据字典：存储每个刻度线旁边的动态文本对象
    dynamic_labels = {}
    TICK_SPACING = 28.8

    for i in range(-25, 26):
        y = cy - (i * TICK_SPACING)

        # 绘制刻度线
        if i == 0:
            canvas.create_line(cx - 30, cy, cx + 30, cy, fill="#00FF00", width=2)
            canvas.create_text(cx + 45, cy, text="0", fill="#00FF00", font=("Arial", 12, "bold"))
        else:
            line_len = 15 if i % 5 == 0 else 8
            color = "#FFFF00" if i > 0 else "#00BFFF"
            canvas.create_line(cx - line_len, y, cx + line_len, y, fill=color, width=1)
            if i % 5 == 0:
                canvas.create_text(cx + line_len + 15, y, text=str(i), fill=color, font=("Arial", 10, "bold"))

        # 在刻度右侧预留悬浮数字的位置
        lbl_id = canvas.create_text(cx + 70, y, text="", fill="white", font=("Arial", 11, "bold"), anchor="w")
        dynamic_labels[i] = lbl_id

    def update_ui():
        global is_expanded, current_distances, is_siege_mode

        # 更新顶部数据
        for i in range(len(labels_text)):
            labels_text[i].set(current_distances[i])

        new_pos = config["ui_pos_small"] if is_expanded else config["ui_pos_tiny"]
        root.geometry(new_pos)

        # 全息阵列渲染逻辑
        if is_siege_mode:
            if siege_win.state() == 'withdrawn':
                siege_win.deiconify()

            # 寻找队伍中第一个有效的标点 (优先自己的黄标)
            active_dist = 0
            active_color = "white"
            for i in range(len(current_distances)):
                if current_distances[i].isdigit() and int(current_distances[i]) > 0:
                    active_dist = int(current_distances[i])
                    active_color = config["markers"][i]["color_hex"]
                    break

            for tick, lbl_id in dynamic_labels.items():
                if active_dist == 0:
                    canvas.itemconfig(lbl_id, text="")  # 没标点时隐藏
                else:
                    dial = calculate_mortar_dial(active_dist, tick)
                    if dial == -1:
                        canvas.itemconfig(lbl_id, text="X", fill="gray")
                    elif dial == active_dist and tick != 0:
                        canvas.itemconfig(lbl_id, text="")  # 过滤无效边缘数据
                    else:
                        canvas.itemconfig(lbl_id, text=f"[{dial}]", fill=active_color)
        else:
            if siege_win.state() == 'normal':
                siege_win.withdraw()

        root.after(30, update_ui)

    root.after(30, update_ui)
    root.mainloop()

# 后台静默扫描线程
def scanner_thread():
    global is_expanded, current_distances, is_macro_running
    markers_ranges = []
    for m in config["markers"]:
        markers_ranges.append((np.array(m["lower_bgr"], dtype=np.uint8), np.array(m["upper_bgr"], dtype=np.uint8)))

    with mss.mss() as sct:
        while True:
            if is_macro_running:
                time.sleep(0.5)
                continue

            if is_expanded:
                current_monitor = config["monitor_small"]
                player_x = config["player_small"]["x"]
                player_y = config["player_small"]["y"]
                multiplier = config["multiplier_small"]
            else:
                current_monitor = config["monitor_tiny"]
                player_x = config["player_tiny"]["x"]
                player_y = config["player_tiny"]["y"]
                multiplier = config["multiplier_tiny"]

            screenshot = np.array(sct.grab(current_monitor))
            frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            temp_distances = ["0", "0", "0", "0"]

            for i, (lower, upper) in enumerate(markers_ranges):
                mask = cv2.inRange(frame, lower, upper)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                valid_contours = []
                for c in contours:
                    if cv2.contourArea(c) < 5:
                        continue
                    x, y, w, h = cv2.boundingRect(c)
                    cx, cy = x + w // 2, y + h // 2
                    center_dist = math.sqrt((cx - player_x)**2 + (cy - player_y)**2)
                    if center_dist < 20 and w < 30 and h < 30:
                        continue
                    valid_contours.append(c)

                if valid_contours:
                    c = max(valid_contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(c)
                    bottom_point = tuple(c[c[:, :, 1].argmax()][0])
                    tip_x, tip_y = bottom_point
                    if tip_y >= current_monitor["height"] - 3:
                        ping_x, ping_y = x + w // 2, y + h // 2
                    else:
                        ping_x, ping_y = tip_x, tip_y

                    pixel_dist = math.sqrt((ping_x - player_x)**2 + (ping_y - player_y)**2)
                    temp_distances[i] = str(max(0, round(pixel_dist * multiplier)))

            current_distances = temp_distances
            time.sleep(0.1)

if __name__ == "__main__":
    print("==================================================")
    print("  PUBG 迫击炮标点测距工具")
    print(f"  物理参数 - 初速: {MORTAR_V} m/s, 重力: {MORTAR_G} m/s²")
    print("==================================================\n")

    keyboard.on_press_key("n", toggle_map_mode)
    keyboard.on_press_key("f9", macro_big_map)
    keyboard.on_press_key("f8", toggle_siege_mode)

    t = threading.Thread(target=scanner_thread, daemon=True)
    t.start()

    create_overlay()
