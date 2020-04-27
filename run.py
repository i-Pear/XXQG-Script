import time

import requests
import os
from PIL import Image
from aip import AipOcr
import copy
import difflib


class Unit:
    def __init__(self, title, choice, ans):
        self.title = title
        self.choice = copy.copy(choice)
        self.ans = ans

    def print(self):
        print(self.title)
        for i in self.choice:
            print(i)
        print(self.ans)


def get_equal_rate(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()


data = []


def load_data():
    with open('db.md', encoding='UTF-8') as f:
        for order in range(1464):
            choice = []
            title = f.readline().replace('_', '').strip()[len(str(order + 1)) + 1:]
            while True:
                temp = f.readline().strip()
                if temp.startswith('答案'):
                    ans = temp
                    break
                else:
                    choice.append(temp)
            data.append(Unit(title, choice, ans))


def get_closest(title) -> Unit:
    global data
    max_val = 0
    res = ""
    title_len = len(title)
    for unit in data:
        simi = get_equal_rate(title, unit.title[:min(len(unit.title), title_len)])
        if simi > max_val:
            max_val = simi
            res = unit
    return res


def get_screenshot():
    # 截屏
    os.popen('adb shell screencap -p /sdcard/image.png').read()
    os.popen('adb pull /sdcard/image.png').read()


def get_word_by_img():
    # 文字识别
    APP_ID = ''
    API_KEY = ''
    SECRET_KEY = ''
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    i = open(r'new_img_fb.png', 'rb')
    img = i.read()
    img_res = client.basicGeneral(img)
    return img_res


lastTitle = ""


def do():
    global lastTitle
    get_screenshot()
    img = Image.open('image.png')
    title_img = img.crop((55, 305, 845, 413))
    title_img.save('new_img_fb.png')
    info = get_word_by_img()['words_result']
    title = ""
    for s in info:
        title += s['words']
    if title == "":
        return
    if title != lastTitle:
        print('\n' * 10)
        print('title=', title)
        lastTitle = title
        res = get_closest(title)
        res.print()
        print('\n' * 2)
    # time.sleep(1)


def run():
    load_data()
    while True:
        try:
            do()
        except Exception:
            pass


if __name__ == '__main__':
    run()
