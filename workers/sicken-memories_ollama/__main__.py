from adistools.adisconfig import adisconfig

from sicken.log import Log
from sicken.events import events
from sicken.DB import DB
from sicken.exceptions import ChatNotFoundException
from sicken.memories import Memories

from ollama import chat
from ollama import ChatResponse

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from json import loads, dumps
from pprint import pprint
from pathlib import Path
from uuid import uuid4
from time import time



class Classification_Ollama:
	project_name="sicken-classifications"

	def __init__(self):
		self._config=adisconfig('/opt/sicken/configs/sicken-ollama_llm.yaml')

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

		self._classification_requests_channel = self._rabbitmq_conn.channel()
		self._classification_requests_channel.basic_consume(
			queue='sicken-classification_requests',
			auto_ack=True,
			on_message_callback=self._classification_request
		)
		

		self._db=DB(self)
		self._events=events(self)

		self._memories=Memories(self)

	def _introduction(self, channel, method, properties, body):
		message=loads(body)
		if message:
			pprint(message)
			self._model_id=message['model_id']
			self._model_name=message['model_name']
			self._actions=message['actions']

			self._gestures_string=self._build_gestures()


	def _build_prompt(self, msg):
		try:
			prompt=[]
			prompt.append(
				{"role": "system", "content": SYSTEM_MESSAGE.replace('<!_gestures_!>', self._gestures_string)}
				)

			previous_messages=self._db.get_chat_messages(
				chat_uuid=msg['chat_uuid']
				)


			for message in previous_messages:
				del message['chat_uuid']
				if message['message_author'] == 'Sicken.ai':
					prompt.append(
						{"role": "assistant", "content": dumps(message)}
						)
				else:
					prompt.append(
						{"role": "user", "content": dumps(message)}
						)

			self._db.add_chat_message(
				chat_uuid=msg['chat_uuid'],
				message_author=msg['message_author'],
				message_source=msg['message_source'],
				msg=msg['message']
				)

			prompt.append({"role": "user", "content": dumps(msg)})

			return prompt
		except:
			self._log.exception('Exception ocured in the build_prompt')
			raise


	def _get_model_response(self, prompt):
		response=chat(
			model=self._config.sicken.model,
			messages=prompt
		)

	   
		resp=response.message.content
		return resp

	def _classification_request(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))

		if message:
			print(self._memories._get_user_memories(
				profile_user_name=message['profile_user_name']))
			


	def start(self):
		self._classification_requests_channel.start_consuming()
		


	def stop(self):
		self._classification_requests_channel.stop_consuming()


if __name__=="__main__":
	classification=Classification_Ollama()
	classification.start()
