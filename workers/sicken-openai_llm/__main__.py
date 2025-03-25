from adistools.adisconfig import adisconfig

from sicken.log import Log
from sicken.events import events
from sicken.DB import DB
from sicken.exceptions import ChatNotFoundException

from constants import SYSTEM_MESSAGE

from openai import OpenAI
from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from json import loads, dumps
from pprint import pprint
from pathlib import Path
from uuid import uuid4
from time import time



class OpenAI_LLM:
	project_name="sicken-openai_llm"

	def __init__(self):
		self._config=adisconfig('/opt/sicken/configs/sicken-openai_llm.yaml')

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

		self._response_requests_channel = self._rabbitmq_conn.channel()
		self._response_requests_channel.basic_consume(
			queue='sicken-response_requests',
			auto_ack=True,
			on_message_callback=self._response_request
		)
		
		self._introduction_channel = self._rabbitmq_conn.channel()
		self._introduction_channel.basic_consume(
			queue='sicken-model_introduction',
			auto_ack=True,
			on_message_callback=self._introduction
		)


		self._db=DB(self)
		self._events=events(self)

		self._openai=OpenAI(api_key=self._config.openai.api_key)

		self._model_name=None
		self._model_id=None
		self._actions=None

		self._events.event(
				event_name="model_introduction_request",
				event_data={}
				)

	def _introduction(self, channel, method, properties, body):
		message=loads(body)
		if message:
			pprint(message)
			self._model_id=message['model_id']
			self._model_name=message['model_name']
			self._actions=message['actions']

			self._gestures_string=self._build_gestures()


	def _build_gestures(self):
		data=[]
		for action_name in self._actions:
			if action_name!="speak":
				data.append({"gesture_name": action_name, "gesture_description": self._actions[action_name]['description']})

		return dumps(data)
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
		completion=self._openai.chat.completions.create(
			model=self._config.sicken.model,
			seed=self._config.sicken.seed,
			frequency_penalty=self._config.sicken.frequency_penalty,
			presence_penalty=self._config.sicken.presence_penalty,
			top_p=self._config.sicken.top_p,
			top_logprobs=self._config.sicken.top_logprobs,
			messages=prompt
		)

	   
		resp=completion.choices[0].message.content
		return resp

	def _response_request(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))

		if not self._model_id and not self._model_name and not self._actions:
			print('Recieved the message request, but the sicken-vtube_plugin didn\'t introduced model and it\'s features. Is the plugin running?')
		
		if message and self._model_id:
			print('Queue message:')
			print(message)
			response_uuid=str(uuid4())

			prompt=self._build_prompt(msg=message)
			print('Prompt:')
			print(prompt)

			print('Json prompt:')
			print(dumps(prompt))


			response=loads(
				self._get_model_response(
					prompt=prompt
				)
			)
			print('Model response:')
			print(response)

			self._db.add_chat_message(
				chat_uuid=message['chat_uuid'],
				message_author='Sicken.ai',
				message_source='OpenAI',
				speech=response['speech'],
				gesture=response['gesture']
				)

			self._events.event(
				event_name="request_responded",
				event_data={
					"response_uuid": response_uuid,
					"chat_uuid": message['chat_uuid'],
					"message_author":message['message_author'],
					"message": message['message'],
					"speech": response['speech'],
					"gesture": response['gesture']
					}
				)
			


	def start(self):
		self._introduction_channel.start_consuming()
		


	def stop(self):
		self._response_requests_channel.stop_consuming()


if __name__=="__main__":
	openai_llm=OpenAI_LLM()
	openai_llm.start()
