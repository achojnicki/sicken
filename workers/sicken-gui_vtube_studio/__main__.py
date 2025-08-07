from sicken.config import Config
from sicken.log import Log
from sicken.GUI.GUI import Sicken_GUI
from sicken.events import events
from sicken.DB import DB

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from uuid import uuid4
from time import time
from threading import Thread
from json import loads

import wx


class Sicken:
	project_name="sicken-gui_vtube_studio"
	def __init__(self):
		self._active=True
		self._config=Config(self)
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

		self._gui_commands_feedback_channel = self.rabbitmq_conn.channel()
		self._gui_commands_feedback_channel.basic_consume(
			queue='sicken-gui_commands_feedback',
			auto_ack=True,
			on_message_callback=self._command_feedback
		)

	def _gui_response(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		if message and message['speech']:
			self._sicken_gui._chat_page.add_sickens_message(message['speech'])

	def _command_feedback(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		if message and message['message']:
			self._sicken_gui._chat_page.add_system_message(message['message'], esc=False)

	def _logs(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		if message:
			wx.CallAfter(
				self._sicken_gui._logs_page._add_item,
				message)

	def start(self):
		self._sicken_gui.Show()

		t=Thread(target=self._gui_commands_feedback_channel.start_consuming, args=[])
		t.daemon=True
		t.start()

		self._app.MainLoop()

if __name__=="__main__":
	app=Sicken()
	app.start()