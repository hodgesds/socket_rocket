from gevent import pywsgi
import gevent
import json

def hello_world(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    counter = 0
    while True:
        yield json.dumps({'a':counter}) + '\n'
        counter += 1
        gevent.sleep(1)
 
server = pywsgi.WSGIServer(
    ('', 8080), hello_world)
 
server.serve_forever()
