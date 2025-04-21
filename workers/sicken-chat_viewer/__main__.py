from adistools.adisconfig import adisconfig
from sicken.log import Log
from sicken.chat_viewer import Chat_Viewer_GUI
from sicken.events import events

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from uuid import uuid4
from time import time
from threading import Thread
from json import loads

import wx


class Chat_Viewer:
	project_name="sicken-chat_viewer"
	def __init__(self):
		self._active=True
		
		self._config=adisconfig('/opt/sicken/configs/sicken-chat_viewer.yaml')

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

		self._chat_viewer_gui=Chat_Viewer_GUI(self)


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

		self._webchat_requests_channel = self.rabbitmq_conn.channel()
		self._webchat_requests_channel.basic_consume(
			queue='sicken-webchat_requests',
			auto_ack=True,
			on_message_callback=self._user_message_request
		)
		
		self._webchat_responses_channel = self.rabbitmq_conn.channel()
		self._webchat_responses_channel.basic_consume(
			queue='sicken-webchat_responses',
			auto_ack=True,
			on_message_callback=self._sicken_message_request
		)

	def _user_message_request(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		if message:
			self._chat_viewer_gui.add_message_user(message)


	def _sicken_message_request(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		if message:
			self._chat_viewer_gui.add_message_sicken(message)
	def start(self):
		self._chat_viewer_gui.Show()

		t=Thread(target=self._webchat_requests_channel.start_consuming, args=[])
		t.daemon=True
		t.start()

		self._app.MainLoop()

if __name__=="__main__":
	app=Chat_Viewer()
	app.start()