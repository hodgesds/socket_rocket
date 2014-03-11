from flask import Flask
from flask_sockets import Sockets
from flask import render_template
import random
import json
import redis

app = Flask(__name__)

REDIS_HOST,REDIS_PORT = '192.168.0.10', 6379

app.debug=True
sockets = Sockets(app)

def grab_ps_data(ps):
    messages = []
    for item in ps.listen():
        if item['type'] == 'message':
            messages.append(item)
            yield item
        else:
            yield None


def grab_stream_data(channel):
    pass
    
@sockets.route('/pub_msg')
def read_socket(ws):
    rpub = redis.client.StrictRedis() #should probably be a config setting...
    while True:
        message = ws.receive()
        if message:
            try:
                data = json.loads(message)
                if 'name' in data.keys() and 'channel' in data.keys():
                    rpub.publish(data['channel'], message)
            except:
                pass
        if ws.closed:
            print 'connection closed'
            break
    
@sockets.route('/sub_msg')
def echo_socket(ws):
    channel = None
    user = None
    rlisten = redis.client.StrictRedis()
    r = redis.client.StrictRedis()
    sub = r.pubsub()
    sub_client = None
    open_channels = ['master']
    while sub_client is None:
        if ws.closed:
            break
        print 'waiting on sub channel'
        message = ws.receive()
        if message:
            try:
                data = json.loads(message)
                if 'subscribe' in data.keys():
                    channel = data['subscribe']
                    user = data['user']
                    open_channels.append(data['subscribe'])
                    sub.subscribe(open_channels)
                    sub_client = grab_ps_data(sub)
                    print 'listenting on channel', data['subscribe']            
            except:
                pass
    while True:
        try:
            i = next(sub_client)
            if i is not None:
                pmess = json.loads(i['data'])
                # we can consume it!
                if user not in pmess['name']:
                    ws.send(json.dumps(i))  
        except:
            pass
        if ws.closed:
            break



@app.route('/<channel>')
def hello(channel):
    lines  = open('names.txt').read().splitlines() 
    name = random.choice(lines) + str(random.randrange(0,1000))
    return render_template('wooper.html',name=name, channel=channel)

@app.route('/')
def home():
    return 'hello'
