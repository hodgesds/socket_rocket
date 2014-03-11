from gevent import pywsgi
from random import uniform, randrange
import gevent
import json


def hello_world(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    w = 900
    h = 400
    x = randrange(0,w)
    y = randrange(0,h)
    data =  {'color': 'hsl(0,0%,28%)', 'xcord': x, 'ycord': y, 'name': 'master', 'channel': 'master'}
    while True:
        #do 10 data points
        x_trend = 5
        y_trend = 5
        for _ in xrange(0,15):
            x_dir = randrange(0,10) > x_trend 
            y_dir = randrange(0,10) > y_trend
            if x_dir:
                x += randrange(0,40)
                x_trend -= 1
            else:
                x -= randrange(0,40)
            if y_dir:
                y += randrange(0,40)
                y_trend -= 1
            else:
                y -= randrange(0,40)
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