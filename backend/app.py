# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29
import sys
if sys.platform == "darwin":
    import selectors
    selectors.DefaultSelector = selectors.PollSelector

import eventlet
import socketio
import agent

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(socketio_app=sio)
bot = agent.Agent("CISCO_BOT", ["help customers solving their problems"])

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.event
def receive(sid, data):
    bot.receive(sio, sid, data)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 12345)), app)