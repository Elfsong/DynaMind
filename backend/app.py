# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29
import sys
if sys.platform == "darwin":
    import selectors
    selectors.DefaultSelector = selectors.PollSelector

import eventlet
socketio = eventlet.import_patched("socketio")

# import socketio
import agent
import kuibu

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(socketio_app=sio, static_files={
    "/": "../frontend/index.html",
    "/cover": "../frontend/cover.html",
    "/img.jpeg": "../frontend/img-1.jpeg",
    "/index.js": "../frontend/index.js",
})

bot = agent.Agent("DYNAMIND_BOT", ["help customers solving their problems"])
# bot = kuibu.KuiBu("DYNAMIND_BOT", ["help customers solving their problems"])


@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.event
def receive(sid, data):
    print("=" * 50)
    if data["token"] == "yyids":
        bot.receive(data["user_input"], socket_config=(sio, sid))
    else:
        print(f"illegal request: {data}")


# @sio.event
# def receive(sid, data):
#     print("=" * 50)
#     step_list = [{
#         "step_description": data["user_input"],
#         "step_result": "None"
#     }]
#     bot.bu(step_list=step_list, recursion_level=0, socket_config=(sio, sid))


if __name__ == '__main__':
    # HTTP
    # eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8443)), app)

    # HTTPS
    eventlet.wsgi.server(
        eventlet.wrap_ssl(
            eventlet.listen(('0.0.0.0', 8443)),
            # certfile='/etc/letsencrypt/live/dynamind.one/fullchain.pem',
            # keyfile='/etc/letsencrypt/live/dynamind.one/privkey.pem',
            certfile='./fullchain.pem',
            keyfile='./privkey.pem',
            server_side=True), 
        app
    )