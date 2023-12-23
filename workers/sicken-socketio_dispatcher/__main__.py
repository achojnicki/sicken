from eventlet import wsgi, monkey_patch
from adisconfig import adisconfig
from log import Log
from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from json import loads, dumps
from flask import Flask, render_template, request
from flask_socketio import SocketIO

import functools

monkey_patch()

class socketio_dispatcher:
    name="sicken-socketio_dispatcher"

    def __init__(self, application, socketio):
        self.application=application
        self.socketio=socketio

        self.config=adisconfig('/opt/adistools/configs/sicken-socketio_dispatcher.yaml')
        self.log=Log(
            parent=self,
            rabbitmq_host=self.config.rabbitmq.host,
            rabbitmq_port=self.config.rabbitmq.port,
            rabbitmq_user=self.config.rabbitmq.user,
            rabbitmq_passwd=self.config.rabbitmq.password,
            debug=self.config.log.debug,
            )

        self.rabbitmq_conn = BlockingConnection(
            ConnectionParameters(
                host=self.config.rabbitmq.host,
                port=self.config.rabbitmq.port,
                credentials=PlainCredentials(
                    self.config.rabbitmq.user,
                    self.config.rabbitmq.password
                )
            )
        )
        self.rabbitmq_channel = self.rabbitmq_conn.channel()

        self.rabbitmq_channel.basic_consume(
            queue='sicken-responses_chat',
            auto_ack=True,
            on_message_callback=self.response_process
        )
        self.bind_socketio_events()

    def response_process(self, channel, method, properties, body):
        data=loads(body.decode('utf8'))
        self.socketio.emit(
            "response",
            data,
            to=data['socketio_session_id']
        )

    def start(self):
        try:
            self.socketio.start_background_task(target=self.rabbitmq_channel.start_consuming)
            self.socketio.run(self.application, host=self.config.socketio.host, port=self.config.socketio.port)
        except:
            self.stop()

    def stop(self):
        self.rabbitmq_channel.stop_consuming()

    def message(self, message):
        message['socketio_session_id']=request.sid
        if message['model']=='sicken-t5':
            q='sicken-requests_t5_chat'

        message=dumps(message)

        self.rabbitmq_conn.add_callback_threadsafe(
            functools.partial(
                self.rabbitmq_channel.basic_publish,
                exchange="",
                routing_key=q,
                body=message))

    def bind_socketio_events(self):
        self.socketio.on_event('message', self.message, namespace="/")

if __name__=="__main__":
    app = Flask(__name__)
    #app.config['SECRET_KEY'] = 'secret!'
    socketio = SocketIO(
        app,
        cors_allowed_origins="*")

    socketio_dispatcher=socketio_dispatcher(app, socketio)
    socketio_dispatcher.start()
