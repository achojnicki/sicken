from adistools.adisconfig import adisconfig
from sicken.log import Log
from sicken.bottom_bar import Bottom_Bar_GUI
from sicken.events import events

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from uuid import uuid4
from time import time
from threading import Thread
from json import loads

import wx

class Bottom_Bar:
	project_name="sicken-bottom_bar"
	def __init__(self):
		self._active=True
		
		self._config=adisconfig('/opt/sicken/configs/sicken-bottom_bar.yaml')

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

		self._bottom_bar_gui=Bottom_Bar_GUI(self)


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

		self._subtitles_channel = self.rabbitmq_conn.channel()
		self._subtitles_channel.basic_consume(
			queue='sicken-subtitles',
			auto_ack=True,
			on_message_callback=self._subtitles
		)
		


	def _subtitles(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		if message:
			self._bottom_bar_gui.add_subtitles(message)
			
	def start(self):
		self._bottom_bar_gui.Show()

		t=Thread(target=self._subtitles_channel.start_consuming, args=[])
		t.daemon=True
		t.start()

		self._app.MainLoop()

if __name__=="__main__":
	app=Bottom_Bar()
	app.start()