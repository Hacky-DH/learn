"""
requires:
pyppeteer>=0.0.25
"""
import asyncio
from .pyppeteer_demo import Demo


class JQ(Demo):

    def __init__(self, _url):
        super().__init__(_url)

    async def main(self):
        await self._init()
        cookies = [
            {
              "name":"u",
              "value":"",
              "domain":"",
              "path":"/",
            }
        ]
        await self.page.setCookie(*cookies)
        await self.page.goto(self.url)
        await self._injection_js()
        cur = await self.page.querySelector('span.tree-curnum')
        await self.random_delay()
        await self.page.screenshot({'path': 'shot.png'})


if __name__ == '__main__':
    url = ''
    jq = JQ(url)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(jq.main())
