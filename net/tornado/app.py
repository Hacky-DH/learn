#!/usr/bin/python

from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

class MainHandler(RequestHandler):
    def get(self):
        self.write("Hello, world")

if __name__ == "__main__":
    app = Application([(r"/", MainHandler),])
    app.listen(8088)
    print('Serving on 8088...')
    IOLoop.current().start()
