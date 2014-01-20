from flask import Flask
from flask_sockets import Sockets
from flask import render_template
import random

app = Flask(__name__)
app.debug=True
sockets = Sockets(app)

@sockets.route('/echo')
def echo_socket(ws):
    while True:
        message = ws.receive()
        print message
        ws.send(message)

@sockets.route('/socket.io/echo')
def poll():
    while True:
        message = ws.receive()
        print message
        ws.send(message)

@app.route('/')
def hello():
    lines  = open('names.txt').read().splitlines() 
    name = random.choice(lines) + str(random.randrange(0,1000))
    return render_template('wooper.html',name=name)
