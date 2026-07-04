import sys
import json
import os
import time
import math
import threading
import mss
import numpy as np
import cv2
import keyboard
import asyncio
import websockets
from pynput.keyboard import Controller as KeyboardController, Key

# ==========================================
# 基础配置
# ==========================================
BASE_RATIO = 1.0          # 距离修正系数（可在 config.json 中配置 calibrate_ratio 覆盖）
PHYSICS_G = 9.8           # 重力加速度 (m/s²)
PHYSICS_V = 82.9          # 迫击炮初速 (m/s)
ENGINE_RUNNING = False

is_expanded = False
is_macro_running = False
is_siege_mode = False
current_distances = ["0", "0", "0", "0"]
kb = KeyboardController()

# ==========================================
# 工具函数
# ==========================================
def log_msg(msg):
    time_str = time.strftime("[%H:%M:%S]")
    print(f"{time_str} {msg}")

# ==========================================
# 核心扫描线程
# ==========================================
def load_config():
    if not os.path.exists("config.json"):
        log_msg("致命错误: 找不到 config.json")
        os._exit(0)
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def scanner_daemon(config):
    global current_distances

    # 读取可选的校准系数
    ratio = config.get("calibrate_ratio", BASE_RATIO)

    markers = [(np.array(m["lower_bgr"], dtype=np.uint8), np.array(m["upper_bgr"], dtype=np.uint8)) for m in config["markers"]]

    with mss.mss() as sct:
        while True:
            if not ENGINE_RUNNING or is_macro_running:
                time.sleep(0.5)
                continue

            monitor = config["monitor_small"] if is_expanded else config["monitor_tiny"]
            px = config["player_small"]["x"] if is_expanded else config["player_tiny"]["x"]
            py = config["player_small"]["y"] if is_expanded else config["player_tiny"]["y"]
            mult = config["multiplier_small"] if is_expanded else config["multiplier_tiny"]

            try:
                frame = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)
                temps = ["0", "0", "0", "0"]
                for i, (lower, upper) in enumerate(markers):
                    mask = cv2.inRange(frame, lower, upper)
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    valids = [c for c in contours if cv2.contourArea(c) >= 5]

                    if valids:
                        c = max(valids, key=cv2.contourArea)
                        x, y, w, h = cv2.boundingRect(c)
                        tx, ty = tuple(c[c[:, :, 1].argmax()][0])
                        ping_x, ping_y = (x + w//2, y + h//2) if ty >= monitor["height"] - 3 else (tx, ty)
                        dist = math.sqrt((ping_x - px)**2 + (ping_y - py)**2)
                        temps[i] = str(max(0, round(dist * mult * ratio)))
                current_distances = temps
            except Exception:
                pass
            time.sleep(1.0 / config.get("scan_fps", 15))

# ==========================================
# WebSocket 数据流服务器
# ==========================================
async def ws_handler(websocket, *args, **kwargs):
    log_msg("前端小组件已连接！开始推送数据...")
    while True:
        if not ENGINE_RUNNING:
            await asyncio.sleep(1)
            continue

        payload = {
            "distances": current_distances,
            "is_siege_mode": is_siege_mode,
            "physics_g": PHYSICS_G,
            "physics_v": PHYSICS_V
        }
        try:
            await websocket.send(json.dumps(payload))
            await asyncio.sleep(0.033)  # 约 30 FPS 刷新率
        except websockets.ConnectionClosed:
            log_msg("前端小组件已断开连接。")
            break

async def main_ws():
    async with websockets.serve(ws_handler, "127.0.0.1", 8899):
        log_msg("WebSocket 引擎已在 ws://127.0.0.1:8899 启动")
        await asyncio.Future()

def start_ws_server():
    try:
        asyncio.run(main_ws())
    except KeyboardInterrupt:
        log_msg("WebSocket 服务器已手动关闭")

# ==========================================
# 热键控制
# ==========================================
def toggle_map(e):
    global is_expanded
    if not keyboard.is_pressed('shift'):
        is_expanded = not is_expanded

def toggle_siege(e):
    global is_siege_mode
    is_siege_mode = not is_siege_mode

# ==========================================
# 启动序列
# ==========================================
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("==========================================")
    print("  Tactical Engine Backend - CLI Mode")
    print("  PUBG Mortar Range Finder")
    print("==========================================\n")

    config = load_config()

    log_msg("引擎启动中...")
    log_msg(f"物理参数 - 重力: {PHYSICS_G} m/s², 初速: {PHYSICS_V} m/s")

    ENGINE_RUNNING = True

    # 注册热键
    keyboard.on_press_key("n", toggle_map)
    keyboard.on_press_key("f8", toggle_siege)

    # 启动扫图线程
    threading.Thread(target=scanner_daemon, args=(config,), daemon=True).start()

    # 启动 WebSocket 服务器 (阻塞主线程)
    log_msg(">>> 后端引擎已完全启动，正在等待前端面板连接...")
    start_ws_server()
