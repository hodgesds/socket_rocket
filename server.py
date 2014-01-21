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
from celery import Celery
from celery.bin import Option

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


PID = os.getpid()

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)

REDIS_HOST = '192.168.0.10'
REDIS_PORT = 6379
app.config['REDIS_HOST'] = '192.168.0.10'
app.config['REDIS_PORT'] = 6379
app.config['BROKER_URL'] = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
BROKER_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)

app.debug=True
sockets = Sockets(app)

def listen(pubsub, channel):
    print 'starting listener'
    for msg in pubsub.listen():
        print "got pubsub message:\n",msg
        gevent.sleep(1)

def callback(channel='test', ws=None):
    print 'listening on channel:', channel
    rconn = redis.Redis(host='localhost', port=6379, db=0)
    pubsub = rconn.pubsub()
    pubsub.subscribe(channel)
    while True:
        for m in pubsub.listen():
            if ws is not None:
                ws.send(m)
                        
@sockets.route('/echo')
def echo_socket(ws):
    rhost = redis.Redis(host='localhost', port=6379, db=0)
    pubsub = rhost.pubsub()
    open_channels = []
    while True:
        message = ws.receive()
        ws.send('woop')
        try:
            data = json.loads(message)
            if 'subscribe' in data.keys():
                if data['subscribe'] not in open_channels:
                    print 'New channel on', data['subscribe']
                    open_channels.append(data['subscribe'])
                    rclient = redis.Redis(host='localhost', port=6379, db=0)
                    clientps = rclient.pubsub()
                    clientps.subscribe(data['subscribe'])
            if 'name' in data.keys() and 'channel' in data.keys():
                rhost.publish(data['channel'], message)
        except:
            pass
        

@sockets.route('/socket.io/echo')
def poll():
    while True:
        message = ws.receive()
        print message
        ws.send(message)

@app.route('/<channel>')
def hello(channel):
    lines  = open('names.txt').read().splitlines() 
    name = random.choice(lines) + str(random.randrange(0,1000))
    return render_template('wooper.html',name=name, channel=channel)
