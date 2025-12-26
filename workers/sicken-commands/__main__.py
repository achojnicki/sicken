
from sicken.config import Config

from sicken.log import Log
from sicken.events import events
from sicken.DB import DB
from sicken.paths import Paths

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from json import loads, dumps
from yaml import safe_load
from uuid import uuid4
from time import time

HELP_MESSAGE_ROOT="""\
<b>Help:</b>
<ul>
{items}
</ul>
"""
HELP_MESSAGE_ITEM="""\
<li>/{command} {args}- {message}</li>
"""

SINGLE_MESSAGE="""\
/{command} {args}- {message}
"""

ARGS_FORMAT="""[{arg}] """

class Commands:
	project_name="sicken-commands"

	def __init__(self):
		self._config=Config(self)

		self._log=Log(
			parent=self,
			rabbitmq_host=self._config.rabbitmq.host,
			rabbitmq_port=self._config.rabbitmq.port,
			rabbitmq_user=self._config.rabbitmq.user,
			rabbitmq_passwd=self._config.rabbitmq.password,
			debug=self._config.log.debug,
			)


		self._rabbitmq_conn = BlockingConnection(
			ConnectionParameters(
				host=self._config.rabbitmq.host,
				port=self._config.rabbitmq.port,
				credentials=PlainCredentials(
					self._config.rabbitmq.user,
					self._config.rabbitmq.password
				)
			)
		)

		self._command_requests_channel = self._rabbitmq_conn.channel()
		self._command_requests_channel.basic_consume(
			queue='sicken-command_requests',
			auto_ack=True,
			on_message_callback=self._command_request
		)

		self._command_feedback_channel = self._rabbitmq_conn.channel()
		self._command_feedback_channel.basic_consume(
			queue='sicken-command_feedback',
			auto_ack=True,
			on_message_callback=self._command_feedback
		)

		self._db=DB(self)
		self._events=events(self)
		self._paths=Paths()

		with open(self._paths('COMMANDS_HELP_FILE'), 'r') as file:
			self._help_messages=safe_load(file)

		print(self._help_messages)


	def _format_args(self, args):
		if args:
			_args=""
			for arg in args:
				_args+=(ARGS_FORMAT.format(arg=arg))
		else:
			_args=" "
		return _args
	def _format_help_message_item(self, command, args, message):
		_args=self._format_args(args)

		return HELP_MESSAGE_ITEM.format(
			command=command,
			args=_args,
			message=message,)

	def _get_help_message(self):
		items=""
		for item in self._help_messages:
			items+=self._format_help_message_item(
				command=item,
				args=self._help_messages[item]['args'],
				message=self._help_messages[item]['message']
				)
		return HELP_MESSAGE_ROOT.format(items=items)

	def _get_single_help_message(self, item):
		return HELP_MESSAGE_ROOT.format(
			items=SINGLE_MESSAGE.format(
				command=item,
				args=self._format_args(self._help_messages[item]['args']),
				message=self._help_messages[item]['message']
				)
			)


	def _command_feedback(self, channel, method, properties, body):
		try:		
			message=loads(body.decode('utf8'))
			if message:
				self._events.event(
					event_name='command_feedback',
					event_data={
						"message": message['message'],
						"escape": False
						}
				)
		except:
			self._log.exception('Exception occured')
			raise
			
	def _command_request(self, channel, method, properties, body):
		try:		
			message=loads(body.decode('utf8'))
			
			if message['cmd'] == 'help':
				if len(message['args']) == 0:
					self._events.event(
						event_name='command_feedback',
						event_data={
							"message": self._get_help_message(),
							"escape": False
							}
						)
				elif len(message['args']) == 1:
					self._events.event(
						event_name='command_feedback',
						event_data={
							"message": self._get_single_help_message(message['args'][0]),
							"escape": False
							}
						)
			if message['cmd'] == 'credits' or message['cmd'] == 'credit':
				if len(message['args'])==0:
					self._events.event(
						event_name="command_feedback",
						event_data={
							"message": "Sicken App by Adrian Chojnicki.<br>Live2D model by Introvert Studio Limited.<br>Sicken is based on an Open Source software.",
							"escape": False
						})
			if message['cmd'] == 'load_model':
				if len(message['args'])==1:
					self._events.event(
                        event_name="load_model",
                        event_data={
                            "model": message['args'][0],
                          }
                        )
			elif message['cmd'] == 'gesture':
				respone_uuid=str(uuid4())
				if len(message['args'])==1:
					self._events.event(
						event_name="gesture",
						event_data={
							"response_uuid": respone_uuid,
							"chat_uuid": None,
							"message_author": "Sicken.ai",
							"message": None,
							"speech": None,
							"gesture": message['args'][0]
						}
					)
		except:
			self._log.exception('Exception occured')
			raise


	def start(self):
		self._command_requests_channel.start_consuming()
		

	def stop(self):
		self._command_requests_channel.stop_consuming()


if __name__=="__main__":
	openai_llm=Commands()
	openai_llm.start()
