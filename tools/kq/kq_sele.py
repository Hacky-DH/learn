# -*- coding: utf-8 -*-
import sys
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


def kq(**kwargs):
    """
    :param kwargs:
        url
        username
        password
    :return:
    """
    option = ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    # need download chromedriver
    driver = Chrome('chromedriver.exe', options=option)
    try:
        url = kwargs.pop('url')
        username = kwargs.pop('username')
        password = kwargs.pop('password')
        driver.get(url)
        random_delay()
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


def run(hour, minute=None, **kwargs):
    """
    :param hour
    :param minute: int or list or tuple
    :param kwargs:
        url
        username
        password
    :return:
    """
    s = sched.scheduler(time.time, time.sleep)
    if minute is None:
        minute = random.randint(10, 59)
    if isinstance(minute, tuple) or isinstance(minute, list):
        minute = random.randint(minute[0], minute[1])
    sec = random.randint(10, 59)
    now = datetime.now()
    dt = now.replace(hour=hour, minute=minute, second=sec)
    tm = dt.strftime('%Y-%m-%d %H:%M:%S')

    def _run():
        res = kq(**kwargs)
        logging.info('run at {} {}'.format(tm, res))

    if dt > now and now.weekday() != 6:
        logging.info('next run will at {}'.format(tm))
        s.enterabs(datetime.timestamp(dt), 0, _run)
        s.run()
        return True
    logging.warning('NOT run at past time {}'.format(tm))
    return False


def parse_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.load(f)


def main(config_file):
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)
    options = parse_config(config_file)
    if options.get('one_shot'):
        if options.get('run_time') == 'now':
            logging.info('run now')
            kq(**options)
        else:
            logging.info('run one shot')
            run(options.get('hour1'), options.get('minute1'), **options)
    else:
        logging.info('run forever')
        while True:
            r1 = run(options.get('hour1'), options.get('minute1'), **options)
            r2 = run(options.get('hour2'), options.get('minute2'), **options)
            if not r1 and not r2:
                logging.info('no plan to run, delay...')
                random_delay(options.get('delay_m')[0] * 60,
                             options.get('delay_m')[1] * 60)


if __name__ == '__main__':
    config = sys.argv[1] if len(sys.argv) > 1 else 'config.yaml'
    main(config)
