from log import Log
from adisconfig import adisconfig
from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from speech_recognition import Recognizer, Microphone


class speech_recognition:
    def __init__(self):
        self.active=True

        self.config = adisconfig('/opt/adistools/configs/sicken-speech_recognition.yaml')
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

        self.recognizer = Recognizer()

    def start(self):
        self.listen()
    
    def stop(self):
        self.active=False


    def listen(self):
        while self.active:
            with Microphone() as source:
                audio = self.recognizer.listen(source)
                try:
                    text=self.recognizer.recognize_google(audio)

                    print(text)
                    self.rabbitmq_channel.basic_publish(
                        exchange="",
                        routing_key="sicken-requests_t5_spoken",
                        body=text)
                except:
                    pass


if __name__=="__main__":
    worker=speech_recognition()
    worker.start()