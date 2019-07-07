"""
selenium

anti selenium js vars:
navigator.webdriver: normal:undefined, selenium:true
navigator.languages: normal:zh-CN
navigator.plugins.length : normal:3
navigator.plugins
solution: https://mp.weixin.qq.com/s/TqL3OawPe9zW_nneyXvefQ

requires:
selenium>=3.141.0
"""
import sys
import random
import time
# help https://www.seleniumhq.org/docs/03_webdriver.jsp
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys


def random_delay(a=5, b=10):
    time.sleep(int(random.uniform(a, b)))


def login(driver, url, username, password):
    driver.get(url)
    random_delay()
    try:
        """
        find the elements:
            find_element_by_id
            find_element_by_class_name
            find_elements_by_class_name
            find_element_by_tag_name
            find_element_by_name
            find_element_by_link_text
            find_element_by_css_selector
        element method:
            click
            submit
            clear
            send_keys
        cookie
            add_cookie(dict)
            get_cookies
            delete_cookie
            delete_all_cookies
        Using JavaScript:
            execute_script
        """
        user = driver.find_element_by_id('username')
        user.clear()
        user.send_keys(username)
        random_delay(1, 5)
        pwd = driver.find_element_by_id('password')
        pwd.clear()
        pwd.send_keys(password)
        random_delay(1, 5)
        pwd.send_keys(Keys.RETURN)
        return '{} login successfully'.format(username)
    except:
        return '{} login failed'.format(username)


option = ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
# need download chromedriver
bs = Chrome('chromedriver.exe', options=option)
random_delay()
bs.maximize_window()
random_delay()
bs.quit()
