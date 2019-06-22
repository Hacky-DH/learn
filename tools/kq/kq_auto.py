# -*- coding: utf-8 -*-
import time
import win32gui
import webbrowser
import sched
import random
from datetime import datetime
from pywinauto.mouse import click
from pywinauto.keyboard import send_keys
from pywinauto import Desktop, Application
"""
https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html

when the screen is locked, pywinauto.mouse.click will occur error:
There is no active desktop required for moving mouse cursor!
"""

def get_mouse_point():
    return win32gui.GetCursorPos()

def closeTab():
    send_keys('^w')

def ok():
    webbrowser.open('')
    time.sleep(10)
    click('left', (936, 584))
    time.sleep(10)
    click('left', (1340, 511))
    time.sleep(10)
    closeTab()

def run(h, m=None):
    s = sched.scheduler(time.time, time.sleep)
    if m is None:
        m = random.randint(10, 59)
    if isinstance(m, tuple):
        m = random.randint(m[0], m[1])
    sec = random.randint(10, 59)
    dt = time.strftime('%Y-%m-%d', time.localtime())
    tm = '{} {}:{}:{}'.format(dt, h, m, sec)
    print('will at', tm)
    t = time.strptime(tm, '%Y-%m-%d %H:%M:%S')
    t = time.mktime(t)
    s.enterabs(t, 0, ok)
    s.run()
    print(tm, 'done')

def start(url):
    #start google chrome
    chrome_dir = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    chrome = Application(backend='uia')
    chrome.start(chrome_dir + ' --force-renderer-accessibility --incognito --start-maximized ' + url)

#print(get_mouse_point())

run(9, (20,30))
run(21, (40,50))
