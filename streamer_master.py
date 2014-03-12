from gevent import pywsgi
from random import uniform, randrange
import gevent
import json


def hello_world(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    w = 900 # hard coded... ouch
    h = 400
    x = randrange(0,w)
    y = randrange(0,h)
    data =  {'color': 'hsl(0,0%,28%)', 'xcord': x, 'ycord': y, 'name': 'master', 'channel': 'master'}
    while True:
        # do 10 data points
        x_trend = 4
        y_trend = 4
        for _ in xrange(0,10):
            x_dir = randrange(0,10) > x_trend 
            y_dir = randrange(0,10) > y_trend
            if x_dir:
                x += randrange(0,10)
                x_trend -= 1
            else:
                x -= randrange(0,10)
                x_trend += 1
            if y_dir:
                y += randrange(0,10)
                y_trend -= 1
            else:
                y -= randrange(0,10)
                y_trend += 1
            if x>w or x<0:
                x = randrange(0,w)
            if y>h or y<0:
                y = randrange(0,h)
            data['xcord'] = unicode(x)
            data['ycord'] = unicode(y)
            yield json.dumps(data) + '\n'
        gevent.sleep(uniform(0,1))
 
server = pywsgi.WSGIServer(
    ('', 8080), hello_world)
 
server.serve_forever()
