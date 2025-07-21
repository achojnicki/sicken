from sicken.config import Config
from sicken.log import Log
from sicken.GUI.GUI_STANDALONE import Sicken_GUI
from sicken.events import events
from sicken.DB import DB
from sicken.paths import Paths

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from uuid import uuid4
from time import time
from threading import Thread
from json import loads

import wx
import live2d.v3 as live2d

class Sicken:
	project_name="sicken-gui_standalone"
	def __init__(self):
		self._active=True
		
		self._config=Config(self)
		self._paths=Paths()

		self._log=Log(
			parent=self,
			rabbitmq_host=self._config.rabbitmq.host,
			rabbitmq_port=self._config.rabbitmq.port,
			rabbitmq_user=self._config.rabbitmq.user,
			rabbitmq_passwd=self._config.rabbitmq.password,
			debug=self._config.log.debug,
			)
		
		self._app=wx.App()

		self._events=events(self)
		self._db=DB(self)

		self._sicken_gui=Sicken_GUI(self)
		self._chat_uuid=str(uuid4())
		self._db.create_chat(
		            chat_uuid=self._chat_uuid,
		            chat_created=time()
		            )


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

		self._gui_responses_channel = self.rabbitmq_conn.channel()
		self._gui_responses_channel.basic_consume(
			queue='sicken-gui_responses',
			auto_ack=True,
			on_message_callback=self._gui_response
		)

		self._logs_channel=self.rabbitmq_conn.channel()
		self._logs_channel.basic_consume(
			queue='sicken-gui_logs',
			auto_ack=True,
			on_message_callback=self._logs
		)
		self._speech_requests_channel = self.rabbitmq_conn.channel()
		self._speech_requests_channel.basic_consume(
			queue='sicken-standalone_speech_requests',
			auto_ack=True,
			on_message_callback=self._speech_request
		)
		self._speech_generation_finished_channel = self.rabbitmq_conn.channel()
		self._speech_generation_finished_channel.basic_consume(
			queue='sicken-standalone_speech_generation_finished',
			auto_ack=True,
			on_message_callback=self._generation_finished
		)

		self._model_introduction_requests_channel = self.rabbitmq_conn.channel()
		self._model_introduction_requests_channel.basic_consume(
			queue='sicken-model_introduction_requests',
			auto_ack=True,
			on_message_callback=self._model_introduction_request
		)



	def _speech_request(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		self._log.info('Received speech request. Waiting for the sicken-speech_generator to finish generating speech.')
		self._log.debug(message)
		print(message)
		if message:
			self._sicken_gui._chat_page._speeches[message['response_uuid']]={
				"response_uuid": message['response_uuid'],
				"chat_uuid": message['chat_uuid'],
				"message_author": message['message_author'],
				"message": message['message'],
				"speech": message['speech'],
				"gesture": message['gesture']
			}

			if not message['speech'] and message['gesture']:
				actions=[]
				if self._sicken_gui._chat_page._speeches[message['response_uuid']]['gesture']:
					actions.append({
						"action_name":self._sicken_gui._chat_page._speeches[message['response_uuid']]['gesture']
						})
				self._sicken_gui._chat_page._is_speaking=True
				self._sicken_gui._chat_page._animation_model.set_actions(actions=actions)
				self._sicken_gui._chat_page._animation_model.play_actions()
				self._sicken_gui._chat_page._is_speaking=False



	def _model_introduction_request(self, channel, method, properties, body):
		self._log.info('Received Vtube Model introduction request. Sending...')
		self._events.event(
				event_name="model_introduction",
				event_data={
					"model_name": self._sicken_gui._chat_page._live2d_model_manifest['model']['name'],
					"model_id": self._sicken_gui._chat_page._live2d_model_manifest['model']['model_id'],
					"actions": self._sicken_gui._chat_page._live2d_model_manifest['actions']
					}
				)
		self._log.success('Vtube Model introduction request answered successfully.')

	def _generation_finished(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		self._log.info('Received generation_finished signal. Starting playing voice and animations')
		self._log.debug(message)
		print(message)
		if message:
			if message['response_uuid'] in self._sicken_gui._chat_page._speeches:
				actions=[]
				if self._sicken_gui._chat_page._speeches[message['response_uuid']]['speech'] and self._config.live2d.whisper_lip_data:
					actions.append({
						"action_name":"speak",
						"words": message['speech_words'],
						"duration": message['speech_duration']
						})

				if self._sicken_gui._chat_page._speeches[message['response_uuid']]['gesture']:
					actions.append({
						"action_name":self._sicken_gui._chat_page._speeches[message['response_uuid']]['gesture']
						})

				self._sicken_gui._chat_page._speeches[message['response_uuid']]['actions']=actions
				if not self._sicken_gui._chat_page._is_speaking:
					self._sicken_gui._chat_page._is_speaking=True
					self._sicken_gui._chat_page._animation_model.set_actions(actions=actions)
					self._sicken_gui._chat_page.play_sound(self._sicken_gui._chat_page._speech_dir.joinpath(f"{message['response_uuid']}.mp3"))
					self._sicken_gui._chat_page._animation_model.play_actions()
					self._sicken_gui._chat_page._is_speaking=False

					del self._sicken_gui._chat_page._speeches[message['response_uuid']]

				else:
					self._sicken_gui._chat_page._awaiting.append(message['response_uuid'])

	def _gui_response(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		print(message)
		if message and message['speech']:
			self._sicken_gui._chat_page.add_sickens_message(message['speech'])

	def _logs(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		if message:
			wx.CallAfter(
				self._sicken_gui._logs_page._add_item,
				message)

	def start(self):
		self._sicken_gui.Show()

		t=Thread(target=self._model_introduction_requests_channel.start_consuming, args=[])
		t.daemon=True
		t.start()

		wx.CallLater(100,self._sicken_gui._chat_page.init_canvas)
		self._app.MainLoop()

if __name__=="__main__":
	live2d.init()
	app=Sicken()
	app.start()