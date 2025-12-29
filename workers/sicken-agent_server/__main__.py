from eventlet import wsgi, monkey_patch
from sicken.config import Config
from sicken.log import Log
from sicken.events import events

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from json import loads, dumps
from time import sleep, time
from uuid import uuid4
from threading import Lock

monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO

import functools



class agent_server:
	project_name="sicken-agent_server"

	def __init__(self, application, socketio):
		self.application=application
		self.socketio=socketio

		self._config=Config(self)
		self.log=Log(
			parent=self,
			rabbitmq_host=self._config.rabbitmq.host,
			rabbitmq_port=self._config.rabbitmq.port,
			rabbitmq_user=self._config.rabbitmq.user,
			rabbitmq_passwd=self._config.rabbitmq.password,
			debug=self._config.log.debug,
			)


		self.application.config['SECRET_KEY'] = self._config.agent_server.secret

		self._commands={}
		self._commands_lock=Lock()
		
		self._processes={}
		self._processes_lock=Lock()

		self._agents={}
		self._sid2agent_uuid={}

		self._agents_lock=Lock()
		self._sid2agent_uuid_lock=Lock()

		self._events=events(self)

		self.bind_socketio_events()

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

		self.agent_command_execution_requests_channel = self.rabbitmq_conn.channel()
		self.agent_command_execution_requests_channel.basic_consume(
			queue='sicken-agent_command_execution_requests',
			auto_ack=True,
			on_message_callback=self._command_execution_request
		)

		self.agent_spawn_proceses_requests_channel = self.rabbitmq_conn.channel()
		self.agent_spawn_proceses_requests_channel.basic_consume(
			queue='sicken-agent_spawn_proceses_requests',
			auto_ack=True,
			on_message_callback=self._spawn_process_request
		)

		self.agent_terminal_snapshot_request_channel = self.rabbitmq_conn.channel()
		self.agent_terminal_snapshot_request_channel.basic_consume(
			queue='sicken-agent_terminal_snapshot_requests',
			auto_ack=True,
			on_message_callback=self._terminal_snapshot_request
		)

		self.agent_terminal_characters_request_channel = self.rabbitmq_conn.channel()
		self.agent_terminal_characters_request_channel.basic_consume(
			queue='sicken-agent_terminal_characters_requests',
			auto_ack=True,
			on_message_callback=self._terminal_characters_request
		)

	
	def start(self):
		try:
			self.socketio.start_background_task(target=self.agent_terminal_characters_request_channel.start_consuming)
			self.socketio.start_background_task(target=self._agents_checker)

			self.socketio.run(self.application, host=self._config.agent_server.host, port=self._config.agent_server.port)
		except:
			raise
			self.stop()


	def stop(self):
		self.agent_command_execution_requests_channel.stop_consuming()




		
	def _agents_checker(self):
		while True:
			try:
				for agent in self._agents:
					if self._agents[agent]['last_ping']:
						if time() - self._agents[agent]['last_ping']>=10:
							print('removing agent', self._agents[agent]['sid'])
							with self._sid2agent_uuid_lock:
								del self._sid2agent_uuid[self._agents[agent]['sid']]

							with self._agents_lock:
								del self._agents[agent]['sid']

				self.socketio.sleep(0.1)
			except RuntimeError:
				pass

	def _connect(self):
		print("connect", request.sid)


	def _agent_connect(self):
		agent_uuid=str(uuid4())

		with self._agents_lock:
			self._agents[agent_uuid]={"agent_uuid": agent_uuid,"sid": request.sid,  "last_ping": None}

		with self._sid2agent_uuid_lock:
			self._sid2agent_uuid[request.sid]=agent_uuid


		print('agent_connect', agent_uuid, request.sid)


	def _ping(self, data=None):
		if request.sid in self._sid2agent_uuid:
			agent_uuid=self._sid2agent_uuid[request.sid]
			if agent_uuid in self._agents:
				with self._agents_lock:
					self._agents[agent_uuid]['last_ping']=time()
				print('agent_ping', agent_uuid, request.remote_addr)


	def _spawn_process_request(self, channel, method, properties, body):
		data=loads(body.decode('utf8'))
		process_uuid=data['process_uuid']

		with self._processes_lock:
			self._processes[process_uuid]={
				"process_uuid": process_uuid,
				"command": data['command']
			}
		
		for agent in self._agents:
			print("sid", self._agents[agent]['sid'])

			self.socketio.emit(
				'spawn_process_request',
					{
					"process_uuid": self._processes[process_uuid]['process_uuid'],
					"command": self._processes[process_uuid]['command']
					},
				to=self._agents[agent]['sid']
				)

	def _terminal_snapshot_request(self, channel, method, properties, body):
		data=loads(body.decode('utf8'))
		process_uuid=data['process_uuid']

		
		for agent in self._agents:
			print("sid", self._agents[agent]['sid'])

			self.socketio.emit(
				'terminal_snapshot_request',
					{
					"process_uuid": self._processes[process_uuid]['process_uuid'],
					},
				to=self._agents[agent]['sid']
				)

	def _terminal_characters_request(self, channel, method, properties, body):
		data=loads(body.decode('utf8'))
		process_uuid=data['process_uuid']
		characters_string=data['characters_string']

		
		for agent in self._agents:
			print("sid", self._agents[agent]['sid'])

			self.socketio.emit(
				'terminal_characters_request',
					{
					"process_uuid": self._processes[process_uuid]['process_uuid'],
					"characters_string": characters_string
					},
				to=self._agents[agent]['sid']
				)

	def _process_terminal_snapshot_response(self, data):
		print(data)
		self._events.event(
			event_name="terminal_snapshot",
			event_data={
				"process_uuid": data['process_uuid'],
				"command": data['command'],
				"terminal_snapshot": data['terminal_snapshot'],
				"status": data['status'],
				"exit_code": data['exit_code']
				}
			)

	def _command_execution_request(self, channel, method, properties, body):
		data=loads(body.decode('utf8'))
		command_uuid=data['command_uuid']
		with self._commands_lock:
			self._commands[data['command_uuid']]={
				"command_uuid": data['command_uuid'],
				"command": data["command"],
				"exitcode": None,
				"stdout": None,
				"stderr": None
			}

		for agent in self._agents:
			print("sid", self._agents[agent]['sid'])
			self.socketio.emit(
				'command_request',
					{
					"command_uuid": self._commands[command_uuid]['command_uuid'],
					"command": self._commands[command_uuid]['command']
					},
				to=self._agents[agent]['sid']
				)


	def _command_response(self, data):
		print(data)
		self._events.event(
			event_name="command_executed",
			event_data={
				"command_uuid": data['command_uuid'],
				"command": data['command'],
				"exit_code": data['exit_code'],
				"stdout": data['stdout'],
				"stderr": data['stderr']
				
				}
			)

	def bind_socketio_events(self):
		self.socketio.on_event('connect', self._connect, namespace="/")

		self.socketio.on_event('agent_connect', self._agent_connect, namespace="/")
		self.socketio.on_event('agent_ping', self._ping, namespace="/")
		self.socketio.on_event('command_response', self._command_response, namespace="/")
		self.socketio.on_event('terminal_snapshot_response', self._process_terminal_snapshot_response, namespace="/")




if __name__=="__main__":
	app = Flask(__name__)
	socketio = SocketIO(
		app,
		#cors_allowed_origins="https://demo.songrequest.co.uk"
		cors_allowed_origins="*"
		)

	bns=agent_server(app, socketio)
	bns.start()
