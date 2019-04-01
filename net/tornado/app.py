#!/usr/bin/python

from tornado.web import Application, RequestHandler, URLSpec
from tornado.ioloop import IOLoop


class MainHandler(RequestHandler):
    def get(self):
        self.write('''<h1>Book store</h1>
        <a href="{}">book1</a>
        <a href="{}">book2</a>
        '''.format(self.reverse_url("book", "0"),
                   self.reverse_url("book", "1")))


class BookHandler(RequestHandler):
    def initialize(self, all_books):
        self.all_books = all_books

    def get(self, id):
        self.write('This is book {}'.format(self.all_books[int(id)]))


if __name__ == "__main__":
    all_books = ['Three days to see', 'Deep learning']
    # list of URLSpec(url regexp, handler)
    app = Application([
        URLSpec(r'/', MainHandler),
        URLSpec(r'/book/([0-9]+)', BookHandler, dict(all_books=all_books), name="book")
    ])
    app.listen(8088)
    print('Serving on 8088...')
    IOLoop.current().start()
