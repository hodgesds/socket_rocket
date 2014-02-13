from flask import Flask
from flask_sockets import Sockets
from flask import render_template
import gevent
import random
import json
import redis
import threading
from time import sleep
import os

PID = os.getpid()

app = Flask(__name__)

REDIS_HOST = '192.168.0.10'
REDIS_PORT = 6379
app.config['REDIS_HOST'] = '192.168.0.10'
app.config['REDIS_PORT'] = 6379
app.config['BROKER_URL'] = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
BROKER_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)

app.debug=True
sockets = Sockets(app)

def listen(n, channel):
  for x in range(n):
    t = threading.Thread(target=callback, args=(channel,))
    t.setDaemon(True)
    t.start()


def callback(channel):
    print 'listening on channel:', channel
    r = redis.client.StrictRedis()
    sub = r.pubsub()
    sub.subscribe(channel)
    messages = []
    while True:
        for m in sub.listen():
            print 'got message',m
                    
#rhost = redis.Redis(host='localhost', port=6379, db=0)
#pubsub = rhost.pubsub()



def grab_ps_data(ps):
    messages = []
    for item in ps.listen():
        if item['type'] == 'message':
            messages.append(item)
            yield item
        else:
            yield None


@sockets.route('/echo')
def echo_socket(ws):
    channel = ''
    r = redis.client.StrictRedis()
    rpub = redis.client.StrictRedis()
    sub = r.pubsub()
    sub_client = None
    open_channels = []
    while True:
        message = ws.receive()
        if message:
            try:
                data = json.loads(message)
                if 'subscribe' in data.keys():
                    channel = data['subscribe']
                    open_channels.append(data['subscribe'])
                    sub.subscribe(open_channels)
                    if sub_client is None:
                        sub_client = grab_ps_data(sub)
                if 'name' in data.keys() and 'channel' in data.keys():
                    rpub.publish(data['channel'], message)
            except:
                pass
        try:
            if sub_client is not None:
                x = 1
                while True:
                    i = next(sub_client)
                    if i is not None:
                        pmess = json.loads(i['data'])
                        # ignore our own spam
                        if data['name'] in pmess['name']:
                            # republish it.... :p
                            rpub.publish(channel, i)
                            continue
                        else:
                            # we can consume it!
                            ws.send(json.dumps(i))  
                    else:
                        break
        except:
            pass



@app.route('/<channel>')
def hello(channel):
    lines  = open('names.txt').read().splitlines() 
    name = random.choice(lines) + str(random.randrange(0,1000))
    return render_template('wooper.html',name=name, channel=channel)
