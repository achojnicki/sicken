from adistools.adisconfig import adisconfig

from pymongo import MongoClient
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from json import loads
from uuid import uuid4


class log_worker:
    mongo_cli = None
    rabbitmq_conn = None

    def __init__(self):
        self._config=adisconfig('/opt/sicken/configs/sicken-log_worker.yaml')

        self._init_mongo()
        self._init_rabbitmq()

    def _init_mongo(self):
        self._mongo_cli = MongoClient(
            self._config.mongo.host,
            self._config.mongo.port
        )
        self._mongo_db = self._mongo_cli[self._config.mongo.db]
        self._mongo_collection = self._mongo_db['logs']

    def _init_rabbitmq(self):
        self._rabbitmq_conn = BlockingConnection(
            ConnectionParameters(
                host=self._config.rabbitmq.host,
                port=self._config.rabbitmq.port,
                credentials=PlainCredentials(
                    self._config.rabbitmq.user,
                    self._config.rabbitmq.password
                )
            )
        )
        self._rabbitmq_channel = self._rabbitmq_conn.channel()

        self._rabbitmq_channel.basic_consume(
            queue='sicken-logs',
            auto_ack=True,
            on_message_callback=self._callback
        )

    def _callback(self, channel, method, properties, body):

        msg = body.decode('utf-8')
        msg = loads(msg)

        log_item_uuid = str(uuid4())
        msg['log_item_uuid'] = log_item_uuid

        self._mongo_collection.insert_one(msg)

    def start(self):
        self._rabbitmq_channel.start_consuming()


if __name__ == "__main__":
    log_worker = log_worker()
    log_worker.start()
