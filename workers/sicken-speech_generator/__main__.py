from adistools.adisconfig import adisconfig

from sicken.log import Log
from sicken.events import events

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from json import loads, dumps
from pprint import pprint
from pathlib import Path
from uuid import uuid4
from os import mkdir
from openai import OpenAI

import requests

class Speech_Generator:
	project_name="sicken-speech_generator"

	def __init__(self):
		self._config=adisconfig('/opt/sicken/configs/sicken-speech_generator.yaml')

		self._log=Log(
			parent=self,
			rabbitmq_host=self._config.rabbitmq.host,
			rabbitmq_port=self._config.rabbitmq.port,
			rabbitmq_user=self._config.rabbitmq.user,
			rabbitmq_passwd=self._config.rabbitmq.password,
			debug=self._config.log.debug,
			)

		self._openai=OpenAI(api_key=self._config.openai.api_key)

		self._rabbitmq_conn = BlockingConnection(
			ConnectionParameters(
				heartbeat=0,
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
			queue='sicken-speech_requests',
			auto_ack=True,
			on_message_callback=self._speech_request
		)

		self._speech_dir=Path(self._config.directories.speech)
		self._events=events(self)


	def _notify_vtube_plugin(self, response_uuid, speech_duration, speech_words):
		self._events.event(
			event_name="speech_generated",
			event_data={
				"response_uuid": response_uuid,
				"speech_duration": speech_duration,
				"speech_words": speech_words
				}
			)
		

	def _speech_request(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))

		if message and message['speech']:

			print(message['speech'])
			response = self._openai.audio.speech.create(
				model=self._config.openai.tts_model,
				voice=self._config.openai.tts_voice,
				input=message['speech'],
			)

			file=self._speech_dir.joinpath(f"{message['response_uuid']}.mp3")
			response.write_to_file(file)

			words=None
			duration=None
			if self._config.speech.whisper_lip_data:
				transcription = self._openai.audio.transcriptions.create(
					model=self._config.openai.transcription_model,
					file=file,
					response_format="verbose_json",
					timestamp_granularities=["word"]
				)

				words=[]
				for word in transcription.words:
					words.append(dict(word))

				duration = transcription.duration

			self._notify_vtube_plugin(message['response_uuid'], duration, words)

	def start(self):
		self._rabbitmq_channel.start_consuming()

	def stop(self):
		self._rabbitmq_channel.stop_consuming()

if __name__=="__main__":
	speech_generator=Speech_Generator()
	speech_generator.start()
