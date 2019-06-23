# -*- coding: utf-8 -*-
import sys
import random
import time
import sched
from datetime import datetime
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys


def random_delay(a=5, b=10):
    time.sleep(int(random.uniform(a, b)))


def kq(url, username, password):
    option = ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    # need download chromedriver
    driver = Chrome('chromedriver.exe', options=option)
    driver.get(url)
    random_delay()
    try:
        user = driver.find_element_by_id('username')
        user.clear()
        user.send_keys(username)
        random_delay(1, 5)
        pwd = driver.find_element_by_id('password')
        pwd.clear()
        pwd.send_keys(password)
        random_delay(1, 2)
        pwd.send_keys(Keys.RETURN)
        random_delay()
        ck = driver.find_element_by_id('clockIn')
        random_delay(2, 5)
        ck.click()
        random_delay()
        return 'done'
    except:
        return 'failed'

def run(h, m=None):
    s = sched.scheduler(time.time, time.sleep)
    if m is None:
        m = random.randint(10, 59)
    if isinstance(m, tuple):
        m = random.randint(m[0], m[1])
    sec = random.randint(10, 59)
    now = datetime.now()
    dt = now.replace(hour=h, minute=m, second=sec)
    tm = dt.strftime('%Y-%m-%d %H:%M:%S')
    def _run():
        res = kq('', '', '')
        print(tm, res)
    if dt > now and now.weekday() != 6:
        print('next will at', tm)
        s.enterabs(datetime.timestamp(dt), 0, _run)
        s.run()
        return True
    return False


while True:
    r1 = run(9, (10, 20))
    r2 = run(21, (30, 40))
    if not r1 and not r2:
        random_delay(10*60, 15*60)
