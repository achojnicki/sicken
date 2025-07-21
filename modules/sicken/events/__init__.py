from .exceptions import EventsFileNotFound, EventNotFound
from sicken.paths import Paths

from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from yaml import safe_load, dump
from json import dumps as json_dumps
from json import loads as json_loads
from pathlib import Path
from pprint import pprint
from datetime import datetime
from platform import system


class AttrDict(dict):
	def __init__(self, *args, **kwargs):
		super(AttrDict, self).__init__(*args, **kwargs)
		self.__dict__ = self     

class events:
	def __init__(self, root ):
		self._events=[]

		self._root=root
		self._config=root._config
		self._log=None
		if hasattr(root,'_log'):
			self._log=root._log

		self._paths=Paths()
		self._events_file=Path(self._paths("EVENTS_FILE_PATH"))

		if self._events_file.is_file():
			if self._log:
				self._log.debug('Events file detected. Opening...')
			self._load_events()
		else:
			raise EventsFileNotFound


	def _open_rabbitmq_connection(self):
		self._rabbitmq_connection=BlockingConnection(
			ConnectionParameters(
				host=self._config.rabbitmq.host,
				port=self._config.rabbitmq.port,
				credentials=PlainCredentials(
					self._config.rabbitmq.user,
					self._config.rabbitmq.password
					)
				))
		
		self._rabbitmq_channel=self._rabbitmq_connection.channel()

	def _close_rabbitmq_connection(self):
		self._rabbitmq_channel.close()
		self._rabbitmq_connection.close()


	def _load_events(self):
		with open(self._events_file,'r') as events_file:
			events_data=safe_load(events_file)
			
			if not self._root.project_name in events_data:
				return

			for event_name in events_data[self._root.project_name]:
				self._events.append(event_name)



	def event(self, event_name, event_data):
		if not event_name in self._events:
			raise EventNotFound

		msg={
			"event_name": event_name,
			"event_source": self._root.project_name,
			"event_data": event_data,
			"event_timestamp": datetime.now().timestamp()
		}

		self._open_rabbitmq_connection()
		self._rabbitmq_channel.basic_publish(
			exchange="",
			routing_key="sicken-events",
			body=json_dumps(msg)
		)
		self._close_rabbitmq_connection()
