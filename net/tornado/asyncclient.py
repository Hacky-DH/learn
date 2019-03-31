#!/usr/bin/python

from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import asyncio

@gen.coroutine
def fetch(url):
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    # Python < 3.3
    # raise gen.Return(response.body)
    # Python >= 3.3
    return response.body

async def main():
	r = await fetch("http://www.example.com")
	print(r)

if __name__ == "__main__":
	asyncio.run(main())