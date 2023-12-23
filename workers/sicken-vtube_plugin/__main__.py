from pika import BlockingConnection, PlainCredentials, ConnectionParameters

from log import Log
from adisconfig import adisconfig

from message import Message
from api_connection import API_Connection

import asyncio


class plugin:
	project_name="sicken-vtube_plugin"

	def __init__(self):
        self.config = adisconfig('/opt/adistools/configs/sicken-vtube_plugin.yaml')
        self.log = Log(
            parent=self,
            rabbitmq_host=self.config.rabbitmq.host,
            rabbitmq_port=self.config.rabbitmq.port,
            rabbitmq_user=self.config.rabbitmq.user,
            rabbitmq_passwd=self.config.rabbitmq.password,
            debug=self.config.log.debug,
            )

        self.api_connection=API_Connection(self)

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
            queue='sicken-model_actions',
            auto_ack=True,
            on_message_callback=self.say
        )



if __name__=="__main__":
	worker=plugin()
	worker.start()



