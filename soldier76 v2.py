import os
import threading
import time
import win32con
import win32gui
import win32ui
import cv2 as cv
import pyttsx3 as pytts
import pyttsx3.drivers
import pyttsx3.drivers.sapi5
from pynput import keyboard
from pynput import mouse
import json
import numpy as np
from slot_info import SlotInfo
from mss import mss
import utils


# --------------------------------------------------
# 全局参数
current_slot = "1"
slot_info = [SlotInfo("", 1), SlotInfo("", 1)]

active_sim = True
active_shot = False
active_ctrl = False
ctr = keyboard.Controller()


# --------------------------------------------------
# 识图
# pos_key in (1, 2) type in (weapon_slot, muzzle, grip, scope, stock)
def similarity(pos_key, pos_type):
    rect = dict_util(pos_type + pos_key, "screen_dict")
    im = screen_shot(rect)
    for item_name in dir_scan(pos_type):
        result = image_similarity_opencv(r"resource\\" + pos_type + r"\\" + item_name + ".png", im)
        if result >= 30:
            return item_name
    return ""


# 对比图片特征点
def image_similarity_opencv(img1, img2):
    image1 = cv.imread(img1, 0)
    image2 = cv.cvtColor(img2, cv.COLOR_RGB2GRAY)

    orb = cv.ORB_create()
    kp1, des1 = orb.detectAndCompute(image1, None)
    kp2, des2 = orb.detectAndCompute(image2, None)
    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
    if des1 is None or des2 is None:
        return 0
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    good_matches = 0
    for m in matches:
        if m.distance <= 50:
            good_matches = good_matches+1
            if good_matches >= 30:
                break
    return good_matches


# 截屏
def screen_shot(rect):
    with mss() as sct:
        shot = sct.grab(rect)
        return np.array(shot.pixels, dtype=np.uint8)


# -------------------------------------------------------------------
# 切换武器
def switch_slot():
    global active_sim
    global current_slot
    global slot_info

    while True:
        if active_sim:
            gun_name = similarity(current_slot, "weapon_slot")
            if gun_name != "":
                slot_info[int(current_slot)-1].gun_name = gun_name
                save_config(slot_info[int(current_slot)-1])
                active_sim = False
            time.sleep(1)


# -------------------------------------------------------------------
# 识别配件
def attachment_lock():
    global slot_info

    slot_list = ("1", "2")
    attach_list = ("muzzle", "grip", "scope", "stock")
    for slot_item in slot_list:
        param = 1
        for attach_item in attach_list:
            attach_name = similarity(slot_item, attach_item)
            param = param * int(dict_util(attach_name, "attach_param"))
        slot_info.slots[slot_item-1] = param


# ------------------------------------------------------------------
def shot_set():
    global active_shot
    global active_ctrl
    global ctr

    while True:
        if active_shot:
            shot_pos = similarity("", "shot_set")
            if "set" == shot_pos and not active_ctrl:
                active_ctrl = True
                ctr.press(keyboard.Key.ctrl)
            elif "stand" == shot_pos and active_ctrl:
                active_ctrl = False
                ctr.release(keyboard.Key.ctrl)

        time.sleep(0.2)


# -------------------------------------------------------------------
# 键盘输入事件
def kb_on_release(key):
    global current_slot
    global active_sim

    try:
        key = str(key.char)
        if key == '1' or key == '2':
            current_slot = key
            active_sim = True
        elif key == "caps_lock":
            attachment_lock()
        elif key == '5':
            save_config(SlotInfo("grenade", 1))
    finally:
        return True


# 键盘监听器
def keyboard_listener():
    kb_listener = keyboard.Listener(on_release=kb_on_release)
    kb_listener.start()


# -------------------------------------------------------------------
# 鼠标输入事件
def ms_on_click(x, y, button, pressed):
    global active_shot
    global active_ctrl

    if str(button) == "Button.left":
        if pressed:
            active_shot = True
        else:
            active_shot = False
            if active_ctrl:
                ctr.release(keyboard.Key.ctrl)


# 鼠标监听器
def mouse_listener():
    ms_listener = mouse.Listener(on_click=ms_on_click)
    ms_listener.start()


# -------------------------------------------------------------------
# 保存配置到D盘根目录
def save_config(slot_item):
    file = "D:\\config.lua"
    with open(file, "w+") as file:
        file.write("fireMode='" + slot_item.gun_name + "'\n fireParam=" + str(slot_item.attach_param))


# 扫描路径
def dir_scan(img_dir):
    filename_list = []
    for files in os.listdir(r'resource\\'+img_dir):
        if os.path.splitext(files)[1] == '.png':
            filename_list.append(os.path.splitext(files)[0])
    return filename_list


# 字典
def dict_util(key, dict_name):
    with open('resource//' + dict_name + '.json', 'r') as f:
        dict_name = json.load(f)
    return dict_name.get(key, key)


# # 初始化
# def init():
#     #加载枪械/配件列表
#     gun_list = dir_scan('resource')
#     muzzle_list = dir_scan('resource//muzzle')


# -------------------------------------------------------------------
# 程序入口
def main():
    os.system("title Solder76 Smart")
    os.system("mode con cols=32 lines=5")
    print("Solder 76 Smart lite")
    print("version 1.0 beta")

    utils.play_sound("Tactical visor activated. ")
    threads = [threading.Thread(target=switch_slot),
               threading.Thread(target=shot_set),
               threading.Thread(target=keyboard_listener),
               # threading.Thread(target=mouse_listener)
    ]
    for t in threads:
        t.start()


if __name__ == '__main__':
    main()