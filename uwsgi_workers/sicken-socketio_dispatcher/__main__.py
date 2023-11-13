import socketio

# create a Socket.IO server
sio = socketio.Server(async_mode='eventlet')

# wrap with a WSGI application
application = socketio.WSGIApp(sio)