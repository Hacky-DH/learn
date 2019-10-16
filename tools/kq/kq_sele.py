# -*- coding: utf-8 -*-
import sys
import random
import time
import sched
import yaml
import logging
from datetime import datetime, timedelta
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys

FORMAT = '%Y-%m-%d %H:%M:%S'

def random_delay(a=5, b=10):
    time.sleep(int(random.uniform(a, b)))

def delay_to_next_day():
    now = datetime.now()
    now_stamp = datetime.timestamp(now)
    now = now + timedelta(days=1)
    dt = now.replace(hour=0, minute=0, second=0)
    logging.info('delay to next day {}'.format(dt.strftime(FORMAT)))
    time.sleep(datetime.timestamp(dt) - now_stamp)

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
    # need download chromedriver and put to PATH
    # http://chromedriver.chromium.org/downloads
    # http://chromedriver.storage.googleapis.com/index.html
    # http://npm.taobao.org/mirrors/chromedriver/
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


def random_time(now, **kwargs):
    """
    random a run time from args
    :param now datetime.now
    :param kwargs:
        hour
        minute
        jitter_minute
    :return: datetime
    """
    hour = kwargs.pop('hour')
    minute = kwargs.get('minute', random.randint(0, 59))
    jitter_minute = kwargs.get('jitter_minute', 10)
    minute += random.randint(-jitter_minute, jitter_minute)
    sec = random.randint(0, 59)
    return now.replace(hour=hour, minute=minute, second=sec)


def _schedule(now, dt, **kwargs):
    """
    :param now datetime.now
    :param dt
    :param kwargs:
        url
        username
        password
    """
    tm = dt.strftime(FORMAT)

    def _run():
        res = kq(**kwargs)
        logging.info('run at {} {}'.format(tm, res))

    if dt > now:
        logging.info('next run will at {}'.format(tm))
        s = sched.scheduler(time.time, time.sleep)
        s.enterabs(datetime.timestamp(dt), 0, _run)
        s.run()
        return True
    logging.warning('NOT run at time {}'.format(tm))
    return False


def schedule(**kwargs):
    """
    :param kwargs:
        url
        username
        password
        hour
        minute
        jitter_minute
    """
    now = datetime.now()
    dt = random_time(now, **kwargs)
    return _schedule(now, dt, **kwargs)


def parse_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.load(f)


def main(config_file):
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)
    options = parse_config(config_file)
    if options.get('one_shot', True):
        logging.info('mode: one shot')
        if options.get('run_time', 'now') == 'now':
            kq(**options)
        else:
            options.update(options.get('start', {}))
            schedule(**options)
    else:
        logging.info('mode: forever')
        while True:
            now = datetime.now()
            exclude_weekdays = options.pop('exclude_weekdays', [5, 6])
            if now.weekday() in exclude_weekdays:
                logging.warning('NOT run at week day {}'.format(now.weekday()+1))
                delay_to_next_day()
                continue
            options.update(options.get('start', {}))
            r_start = schedule(**options)
            options.update(options.get('end', {}))
            r_end = schedule(**options)
            delay_to_next_day()


if __name__ == '__main__':
    config = sys.argv[1] if len(sys.argv) > 1 else 'config.yaml'
    main(config)
