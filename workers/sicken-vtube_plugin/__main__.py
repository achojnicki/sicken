from adistools.adisconfig import adisconfig

from sicken.events import events
from sicken.log import Log

from sicken.Sicken_VTube import API_Connection, Model

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from time import sleep
from json import loads
from pathlib import Path
from threading import Thread
from playsound import playsound
from yaml import safe_load

import sys

class Sicken_VTube_Plugin:
	project_name="sicken-vtube_plugin"

	def __init__(self):
		self._active=True
		self._config = adisconfig('/opt/sicken/configs/sicken-vtube_plugin.yaml')
		self._log = Log(
			parent=self,
			rabbitmq_host=self._config.rabbitmq.host,
			rabbitmq_port=self._config.rabbitmq.port,
			rabbitmq_user=self._config.rabbitmq.user,
			rabbitmq_passwd=self._config.rabbitmq.password,
			debug=self._config.log.debug,
			)


		self._model_path=Path(self._config.directories.live2d_models).joinpath(self._config.model.model).joinpath('model.yaml')
		self._generators_path=Path(self._config.directories.live2d_models).joinpath(self._config.model.model).joinpath('generators.py')
		with open(self._model_path, 'r') as file:
			self._live2d_model_manifest=safe_load(file.read())

		self.rabbitmq_conn = BlockingConnection(
			ConnectionParameters(
				host=self._config.rabbitmq.host,
				port=self._config.rabbitmq.port,
				credentials=PlainCredentials(
					self._config.rabbitmq.user,
					self._config.rabbitmq.password
				)
			)
		)
		self._speech_requests_channel = self.rabbitmq_conn.channel()

		self._speech_requests_channel.basic_consume(
			queue='sicken-vtube_plugin_speech_requests',
			auto_ack=True,
			on_message_callback=self._speech_request
		)
		self._speech_generation_finished_channel = self.rabbitmq_conn.channel()
		self._speech_generation_finished_channel.basic_consume(
			queue='sicken-vtube_plugin_speech_generation_finished',
			auto_ack=True,
			on_message_callback=self._generation_finished
		)

		self._model_introduction_requests_channel = self.rabbitmq_conn.channel()
		self._model_introduction_requests_channel.basic_consume(
			queue='sicken-model_introduction_requests',
			auto_ack=True,
			on_message_callback=self._model_introduction_request
		)

		self._api_connection=API_Connection(self)
		self._model=Model(self)

		self._events=events(self)

		self._speech_dir=Path(self._config.directories.speech)

		self._speeches={}
		self._is_speaking=False
		self._awaiting=[]

		self.awaiting_thread()

		

	def _play_sound(self, file):
		playsound(file)

	def play_sound(self, file):
		t=Thread(target=self._play_sound, args=[file])
		t.start()

	def _awaiting_thread(self):
		while self._active:
			if not self._is_speaking:
				for item in list(self._awaiting):
					actions=self._speeches[item]['actions']

					if not self._is_speaking:
						self._model.set_actions(actions=actions)
						self.play_sound(self._speech_dir.joinpath(f"{item}.mp3"))
						self._model.play_actions(self._live2d_model_manifest['model']['model_id'])

						del self._speeches[item]
						del self._awaiting[self._awaiting.index(item)]
					break
			sleep(1)
	def awaiting_thread(self):
		t=Thread(target=self._awaiting_thread, args=[])
		t.start()

	def _model_introduction_request(self, channel, method, properties, body):
		self._events.event(
				event_name="model_introduction",
				event_data={
					"model_name": self._live2d_model_manifest['model']['name'],
					"model_id": self._live2d_model_manifest['model']['model_id'],
					"actions": self._live2d_model_manifest['actions']
					}
				)

	def _speech_request(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))

		print(message)
		if message:
			self._speeches[message['response_uuid']]={
				"response_uuid": message['response_uuid'],
				"chat_uuid": message['chat_uuid'],
				"message_author": message['message_author'],
				"message": message['message'],
				"speech": message['speech'],
				"gesture": message['gesture']
			}

			if not message['speech'] and message['gesture']:
				actions=[]
				if self._speeches[message['response_uuid']]['gesture']:
					actions.append({
						"action_name":self._speeches[message['response_uuid']]['gesture']
						})
				self._is_speaking=True
				self._model.set_actions(actions=actions)
				self._model.play_actions(self._live2d_model_manifest['model']['model_id'])
				self._is_speaking=False

	def _generation_finished(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		print(message)
		if message:
			if message['response_uuid'] in self._speeches:
				actions=[]
				if self._speeches[message['response_uuid']]['speech'] and self._config.vtube.whisper_lip_data:
					actions.append({
						"action_name":"speak",
						"words": message['speech_words'],
						"duration": message['speech_duration']
						})

				if self._speeches[message['response_uuid']]['gesture']:
					actions.append({
						"action_name":self._speeches[message['response_uuid']]['gesture']
						})

				self._speeches[message['response_uuid']]['actions']=actions
				if not self._is_speaking:
					self._is_speaking=True
					self._model.set_actions(actions=actions)
					self.play_sound(self._speech_dir.joinpath(f"{message['response_uuid']}.mp3"))
					self._model.play_actions(self._live2d_model_manifest['model']['model_id'])
					self._is_speaking=False

					del self._speeches[message['response_uuid']]

				else:
					self._awaiting.append(message['response_uuid'])


	def start(self):
		self._active=True
		self._api_connection.init_connection(
			host=self._config.vtube.host,
			port=self._config.vtube.port)
		self._model.load_model(self._live2d_model_manifest['model']['model_id'])
		
		self._speech_requests_channel.start_consuming()



if __name__=="__main__":
	svp=Sicken_VTube_Plugin()
	svp.start()



