# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29

import eventlet
import socketio

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.event
def message(sid, data):
    print(f'message from {sid}: {data}')
    sio.emit('message', {"style": "primary", "content": data["feedback"]}, room=sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 12345)), app)