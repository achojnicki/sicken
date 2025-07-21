from sicken.config import Config
from sicken.log import Log
from sicken.paths import Paths

from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from yaml import safe_load, dump
from json import dumps as json_dumps
from json import loads as json_loads
from pathlib import Path
from pprint import pprint
from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient
from platform import system

class EventsException(Exception):
	pass

class EventsFileNotFound(Exception):
	pass

class EventNotFound(EventsException):
	pass

class EventParentNotFound(EventsException):
	pass



class Events:
	project_name="sicken-events"
	def __init__(self):
		self._project_events={}
		self._events=[]
		self._destinations=[]

		self._config=Config(self)

		self._log=Log(
			parent=self,
			rabbitmq_host=self._config.rabbitmq.host,
			rabbitmq_port=self._config.rabbitmq.port,
			rabbitmq_user=self._config.rabbitmq.user,
			rabbitmq_passwd=self._config.rabbitmq.password,
			debug=self._config.log.debug,
			)
		self._paths=Paths()

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
		self._rabbitmq_channel.basic_consume(
			queue='sicken-events',
			auto_ack=True,
			on_message_callback=self._event_request
		)

		self._mongo_cli=MongoClient(
			self._config.mongo.host,
			self._config.mongo.port,
		)

		self._mongo_db=self._mongo_cli[self._config.mongo.db]
		self._metrics=self._mongo_db['events_metrics']

		self._events_file=Path(self._paths("EVENTS_FILE_PATH"))
		if self._events_file.is_file():
			self._log.debug('Events file detected. Opening...')
			self._load_events()

	def _add_metric(self, event_uuid, event_source, event_name, event_destination, event_data, event_timestamp):
		document={
			"event_uuid": event_uuid,
			"event_source": event_source,
			"event_name": event_name,
			"event_destination": event_destination,
			"event_data": event_data
			}

		self._metrics.insert_one(document)

	def _translate_mapping(self, destination_index, event_data, event_uuid):
		mapping=self._destinations[destination_index]['event_mapping']
		data={}
		for item in event_data:
			if item in mapping:
				data[mapping[item]]=event_data[item]

		data['event_uuid']=event_uuid
		return data


	def _load_events(self):
		try:
			with open(self._events_file,'r') as events_file:
				events_data=safe_load(events_file)
				
				for project_name in events_data:
					events=[]
					for event_name in events_data[project_name]:

						destinations=[]
						for destination in events_data[project_name][event_name]:
							destination={
								"event_source": project_name,
								"event_name": event_name,
								"event_destination": destination,
								"event_mapping": events_data[project_name][event_name][destination]
							}
							self._destinations.append(destination)
							destinations.append(self._destinations.index(destination))

						event={
							"event_name":event_name,
							"destinations": destinations
						}
						self._events.append(event)
						events.append(self._events.index(event))

					project_event={
						"project_name": "project_name",
						"events": events
					}

					self._project_events[project_name]=project_event
		except:
			self._log.exception("exception occured in the events during parsing events definitions file.", as_fatal=True)



	def _event_request(self, channel, method, properties, body):
		try:
			message=json_loads(body.decode('utf-8'))

			if not message['event_source'] in self._project_events:
				self._log.error(f'Got the event {message["event_name"]} from the {message["event_source"]}, but the source not found in the definitions')
				raise EventParentNotFound
			
			found=False
			for event_index in self._project_events[message['event_source']]['events']:
				
				for destination_index in self._events[event_index]['destinations']:
					destination=self._destinations[destination_index]
					if message['event_name']==destination['event_name']:
						found=True
						event_uuid=str(uuid4())
						time=datetime.now()

						self._log.info(f'Emitting event {event_uuid} {message["event_name"]} to the queue {destination["event_destination"]}.')

						self._add_metric(
							event_uuid=event_uuid,
							event_name=message['event_name'],
							event_destination=destination['event_destination'],
							event_timestamp=time.timestamp(),
							event_data=message['event_data'],
							event_source=message['event_source']
						)

						self._rabbitmq_channel.basic_publish(
							exchange="",
							routing_key=destination['event_destination'],
							body=json_dumps(
								self._translate_mapping(
									destination_index=destination_index,
									event_data=message['event_data'],
									event_uuid=event_uuid
									)
								)
						)
			
			if not found:
				self._log.error(f'Got the {message["event_name"]} event from the {message["event_source"]}, but the event not found in definitions')
				raise EventNotFound
		except:
			self._log.exception("Error occured in events during processing an event", as_fatal=True)



	def start(self):
		self._rabbitmq_channel.start_consuming()

	def stop(self):
		self._rabbitmq_channel.stop_consuming()

if __name__=="__main__":
	events=Events()
	events.start()