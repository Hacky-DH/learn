#!/usr/bin/python

from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado import gen
import sys

PY33 = sys.version_info[:2] >= (3, 3)
PY35 = sys.version_info[:2] >= (3, 5)

URL = "http://www.example.com"

if PY35:
	import asyncio
	async def fetch(url):
		"""use async and await"""
		http_client = AsyncHTTPClient()
		response = await http_client.fetch(url)
		return response.body

	def main():
		content = asyncio.run(fetch(URL))
		print(content[:20])
else:
	@gen.coroutine
	def fetch(url):
		"""
		use yield generator

		:return Future
		"""
		http_client = AsyncHTTPClient()
		response = yield http_client.fetch(url)
		if PY33:
			return response.body
		else:
			raise gen.Return(response.body)

	def main():
		content = IOLoop().run_sync(lambda: fetch(URL))
		print(content[:20])

if __name__ == "__main__":
	main()
