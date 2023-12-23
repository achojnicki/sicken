from log import Log
from adisconfig import adisconfig
from pika import BlockingConnection, PlainCredentials, ConnectionParameters

import pyttsx3


class speech_synth:
    name = "sicken-speech_synth"

    def __init__(self):
        self.config = adisconfig('/opt/adistools/configs/sicken-speech_synth.yaml')
        self.log = Log(
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
            queue='sicken-responses_spoken',
            auto_ack=True,
            on_message_callback=self.say
        )
        self.speech_synth = pyttsx3.init()

    def say(self, channel, method, properties, body):
        text=body.decode('utf8')
        print(text)

        self.speech_synth.say(text)
        self.speech_synth.runAndWait()

    def start(self):
        self.rabbitmq_channel.start_consuming()

    def stop(self):
        self.rabbitmq_channel.stop_consuming()


if __name__=="__main__":
    worker=speech_synth()
    worker.start()