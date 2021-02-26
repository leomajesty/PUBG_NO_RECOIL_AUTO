import os
import threading
import time
import cv2 as cv
import pyttsx3 as pytts
import pyttsx3.drivers
import pyttsx3.drivers.sapi5
from pynput import keyboard
from pynput import mouse
import json
import numpy as np
from tkinter import *
from slot_info import SlotInfo
from mss import mss

# import mss.tools as mss_tools


# --------------------------------------------------
# 全局参数
root = Tk()

current_slot = "1"
slot_info = [SlotInfo("", 1), SlotInfo("", 1)]

active_sim = True  # 识别状态值
active_shot = False  # 射击状态值
active_ctrl = False  # 下蹲状态值

switch_sim = True  # 识别开关

config_key_list = ['Key.f1', 'Key.f2', 'Key.f3', 'Key.f4', 'Key.f5', 'Key.f6', 'Key.f7', 'Key.f8', 'Key.f9', 'Key.f10',
                   'Key.f11', 'Key.f12']
ctr = keyboard.Controller()


# --------------------------------------------------
# 识图
# pos_key in (1, 2) type in (weapon_slot, muzzle, grip, scope, stock)
def similarity(pos_key, pos_type):
    rect = dict_util(pos_type + pos_key, "screen_dict")
    im = np.array(screen_shot(rect).pixels, dtype=np.uint8)
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
            good_matches = good_matches + 1
            if good_matches >= 30:
                break
    return good_matches


# 截屏
def screen_shot(rect):
    with mss() as sct:
        shot = sct.grab(rect)
        # mss_tools.to_png(shot.rgb, shot.size,
        #                  output=r'resource//partialscreen.png')
        return shot


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
                # if gun_name != slot_info[int(current_slot) - 1].gun_name:
                slot_info[int(current_slot) - 1].gun_name = gun_name
                save_config(slot_info[int(current_slot) - 1])
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
            if attach_name != "":
                param = param * int(dict_util(attach_name, "attach_param"))
        slot_info[int(slot_item) - 1].attach_param = param


# ------------------------------------------------------------------
def shot_set():
    global active_shot
    global active_ctrl
    global ctr
    rect_set = dict_util("shot_set", "screen_dict")
    while True:
        if active_shot:
            img_set = screen_shot(rect_set)
            key = is_set(img_set)
            if not key and active_ctrl:
                ctr.release(keyboard.Key.ctrl)
                active_ctrl = False
            elif key and not active_ctrl:
                active_ctrl = True
                ctr.press(keyboard.Key.ctrl)
        elif active_ctrl:
            ctr.release(keyboard.Key.ctrl)
            active_ctrl = False
        time.sleep(0.2)


# 取色
def is_set(img_set):
    for i in (0, 1, 2, 3, 4):
        sum_line = 0
        sum_bottom = 0
        for j in (0, 1, 2):
            if not 175 <= img_set.pixels[2][i][j] <= 250:
                return False
            sum_line = sum_line + img_set.pixels[1][i][j]
            sum_bottom = sum_bottom + img_set.pixels[2][i][j]
        if sum_line > sum_bottom - 200:
            return False
    return True


# -------------------------------------------------------------------
# 键盘输入事件
def kb_on_release(key):
    global current_slot
    global active_sim
    global active_ctrl
    global switch_sim

    try:
        str_key = str(key)
        if str_key == '\'1\'' or str_key == '\'2\'':  # switch weapon slot
            current_slot = key.char
            if switch_sim:
                active_sim = True
            elif '' != slot_info[int(current_slot) - 1].gun_name:
                save_config(slot_info[int(current_slot) - 1])
        # elif key == "Key.caps_lock":
        #     attachment_lock()
        elif str_key == '5':  # grenade mode
            save_config(SlotInfo("grenade", 1))
        elif str_key == 'Key.f1':  # switch sim
            if switch_sim:
                switch_sim = False
                play_sound("Please choose your weapon. ")
            else:
                switch_sim = True
                play_sound("Tactical visor activated. ")
        elif not switch_sim and str_key in config_key_list:  # bind weapon 1config to current slot
            gun_name = dict_util(str_key, "keyboard_dict")
            if str_key != gun_name:
                play_sound("Bind to slot " + current_slot)
                slot_info[int(current_slot) - 1].gun_name = gun_name
                save_config(slot_info[int(current_slot) - 1])
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


# 鼠标监听器
def mouse_listener():
    ms_listener = mouse.Listener(on_click=ms_on_click)
    ms_listener.start()


# -------------------------------------------------------------------
# 保存配置到D盘根目录
def save_config(slot_item):
    if slot_item.gun_name != "":
        print(slot_item.gun_name + " deployed.")
        file = "D:\\config.lua"
        with open(file, "w+") as file:
            file.write("fireMode='" + dict_util(slot_item.gun_name, "gun_dict") +
                       "'\n fireParam=" + str(slot_item.attach_param))
        play_sound(slot_item.gun_name + " deployed.")


# 扫描路径
def dir_scan(img_dir):
    filename_list = []
    for files in os.listdir(r'resource\\' + img_dir):
        if os.path.splitext(files)[1] == '.png':
            filename_list.append(os.path.splitext(files)[0])
    return filename_list


# 字典
def dict_util(key, dict_name):
    with open('resource//' + dict_name + '.json', 'r') as f:
        dict_name = json.load(f)
    return dict_name.get(key, key)


# -------------------------------------------------------------------
# 播放声音
def play_sound(content):
    engine = pytts.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 200)  # 语速
    engine.setProperty('volume', 0.8)  # 音量
    engine.say(content)
    engine.runAndWait()
    engine.stop()
    pass


# -------------------------------------------------------------------
# 程序入口
def main():
    os.system("title Solder76 Smart")
    os.system("mode con cols=32 lines=5")
    print("Solder 76 Smart lite")
    print("version 1.0 beta")

    play_sound("Tactical visor activated. ")
    threads = [threading.Thread(target=switch_slot),
               threading.Thread(target=shot_set),
               threading.Thread(target=keyboard_listener),
               threading.Thread(target=mouse_listener)
               ]
    for t in threads:
        t.start()


if __name__ == '__main__':
    main()
