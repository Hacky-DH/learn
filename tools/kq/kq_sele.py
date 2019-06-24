# -*- coding: utf-8 -*-
import random
import time
import sched
import yaml
import logging
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
    finally:
        driver.quit()


def run(url, username, password, h, m=None):
    s = sched.scheduler(time.time, time.sleep)
    if m is None:
        m = random.randint(10, 59)
    if isinstance(m, tuple) or isinstance(m, list):
        m = random.randint(m[0], m[1])
    sec = random.randint(10, 59)
    now = datetime.now()
    dt = now.replace(hour=h, minute=m, second=sec)
    tm = dt.strftime('%Y-%m-%d %H:%M:%S')

    def _run():
        res = kq(url, username, password)
        logging.info('run at {} {}'.format(tm, res))

    if dt > now and now.weekday() != 6:
        logging.info('next run will at {}'.format(tm))
        s.enterabs(datetime.timestamp(dt), 0, _run)
        s.run()
        return True
    logging.warning('NOT run at past time {}'.format(tm))
    return False


def parse_config(file_name='config.yaml'):
    with open(file_name, 'r') as f:
        return yaml.load(f)


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)
    options = parse_config()
    if options.get('one_shot'):
        if options.get('run_time') == 'now':
            logging.info('run now')
            kq(options.get('url'),
               options.get('username'),
               options.get('password'))
        else:
            logging.info('run one shot')
            run(options.get('url'),
                options.get('username'),
                options.get('password'),
                options.get('hour1'),
                options.get('minute1'))
    else:
        logging.info('run forever')
        while True:
            r1 = run(options.get('url'),
                     options.get('username'),
                     options.get('password'),
                     options.get('hour1'),
                     options.get('minute1'))
            r2 = run(options.get('url'),
                     options.get('username'),
                     options.get('password'),
                     options.get('hour2'),
                     options.get('minute2'))
            if not r1 and not r2:
                logging.info('no plan to run, delay...')
                random_delay(options.get('delay_m')[0] * 60,
                             options.get('delay_m')[1] * 60)


if __name__ == '__main__':
    main()
