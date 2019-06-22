"""
API: https://github.com/GoogleChrome/puppeteer/blob/master/docs/api.md

demo: https://www.icode9.com/content-4-137761.html

requires:
pyppeteer>=0.0.25
"""
import random
import asyncio
import pyppeteer
from win32api import GetSystemMetrics


class Demo:

    def __init__(self, _chrome_exe, _url, _username, _pwd):
        pyppeteer.DEBUG = True
        self.page = None
        self.chrome_exe = _chrome_exe
        self.url = _url
        self.username = _username
        self.pwd = _pwd

    async def _injection_js(self):
        await self.page.evaluate('''() =>{
                   Object.defineProperties(navigator,{
                     webdriver:{
                       get: () => undefined
                     }
                   })
                }''')

        await self.page.evaluate('''() => {
            window.navigator.chrome = {
            runtime: {},
            };
            }''')

        await self.page.evaluate('''() => {
                  const originalQuery = window.navigator.permissions.query;
                  return window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                      Promise.resolve({ state: Notification.permission }) :
                      originalQuery(parameters)
                  );
                }
            ''')

        await self.page.evaluate('''() =>{
            Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
                });
            }''')

        await self.page.evaluate('''() =>{
            Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
                });
            }''')

    async def _init(self):
        browser = await pyppeteer.launch({'headless': False,
                                          'executablePath': self.chrome_exe,
                                          'args': [
                                              '--disable-extensions',
                                              '--hide-scrollbars',
                                              '--disable-bundled-ppapi-flash',
                                              '--mute-audio',
                                              '--no-sandbox',
                                              '--disable-setuid-sandbox',
                                              '--disable-gpu',
                                              '--start-maximized',
                                          ],
                                          'dumpio': True,
                                          })
        self.page = await browser.newPage()
        await self.page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                     '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
        await self.page.setViewport({'width': GetSystemMetrics(0), 'height': GetSystemMetrics(1)})

    async def get_cookie(self):
        cookies_list = await self.page.cookies()
        cookies = ''
        for cookie in cookies_list:
            str_cookie = '{0}={1};'
            str_cookie = str_cookie.format(cookie.get('name'), cookie.get('value'))
            cookies += str_cookie
        print(cookies)
        return cookies

    async def random_delay(self, a=1000, b=5000):
        await self.page.waitFor(random.uniform(a, b))

    async def mouse_slider(self, slider):
        try:
            await self.random_delay()
            await slider.hover()
            # await self.page.hover('div.JDJRV-slide-btn')
            await self.page.mouse.down()
            await self.page.mouse.move(1000, 0, {'steps': 30})
            await self.page.mouse.up()
            await self.random_delay()
            await self.page.screenshot({'path': './headless-slide-result.png'})
        except Exception as e:
            print(e, 'slider login error')
            return False
        else:
            await self.random_delay()
            slider_again = await self.page.querySelectorEval('div.JDJRV-slide-btn', 'node => node.textContent')
            if slider_again != '拼接成功':
                return False
            else:
                return True

    async def main(self):
        await asyncio.sleep(30)
        await self._init()
        await self.page.goto(self.url)
        await self._injection_js()
        ua = await self.page.evaluate('navigator.webdriver')
        print('webdriver', ua)
        # change to username/password login
        await self.page.click('div.login-tab-r')
        await self.random_delay()
        await self.page.type('#loginname', self.username, {'delay': random.randint(100, 151) - 50})
        await self.page.type('#nloginpwd', self.pwd, {'delay': random.randint(100, 151)})
        await self.random_delay()
        # login
        await self.page.keyboard.press('Enter')
        await self.random_delay()
        # slider
        slider = await self.page.querySelector('div.JDJRV-slide-btn')
        if slider:
            res = await self.mouse_slider(slider)
            if not res:
                print('failed to slider')
                return
            await self.page.screenshot({'path': 'failed.png'})
            await self.page.click('div.login-btn')
        await self.random_delay()
        await self.page.screenshot({'path': 'login.png'})
        return 'done'


if __name__ == '__main__':
    chrome_exe = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    url = 'https://passport.jd.com/new/login.aspx'
    username = ''
    pwd = ''
    demo = Demo(chrome_exe, url, username, pwd)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(demo.main())
