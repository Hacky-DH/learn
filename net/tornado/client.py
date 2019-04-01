#!/usr/bin/python

from tornado.httpclient import HTTPClient
import json

if __name__ == "__main__":
    client = HTTPClient()
    response = client.fetch('http://127.0.0.1:8088/book/0')
    assert 'Three days to see' in response.body.decode()

    response = client.fetch('http://127.0.0.1:8088',
                            method='POST',
                            body=json.dumps({'message': 'Hello Tornado'}))
    assert 'Receive Hello Tornado' in response.body.decode()
