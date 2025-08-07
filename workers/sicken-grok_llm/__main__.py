from sicken.config import Config

from sicken.log import Log
from sicken.events import events
from sicken.DB import DB
from sicken.memories import Memories
from sicken.knowledge import Knowledge
from sicken.exceptions import ChatNotFoundException

from constants import SYSTEM_MESSAGE

from openai import OpenAI
from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from json import loads, dumps
from pathlib import Path
from uuid import uuid4
from time import time



class Grok_LLM:
	project_name="sicken-grok_llm"

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

		self._openai=OpenAI(
			api_key=self._config.grok.api_key,
			base_url="https://api.x.ai/v1")

		self._model_name=None
		self._model_id=None
		self._actions=None

		self._memories=Memories(self)
		self._knowledge=Knowledge(self)

		
	def _introduction(self, channel, method, properties, body):
		try:
			self._log.info('Received model introduction response')
			message=loads(body)
			self._log.debug(message)

			if message:
				self._model_id=message['model_id']
				self._model_name=message['model_name']
				self._actions=message['actions']

				self._gestures_string=self._build_gestures()

				self._log.success('Model introduction processed successfully')

		except:
			self._log.exception('Exception occured')
			raise


	def _build_gestures(self):
		try:
			data=[]
			for action_name in self._actions:
				if action_name!="speak":
					data.append({"gesture_name": action_name, "gesture_description": self._actions[action_name]['description']})

			return dumps(data)
		except:
			self._log.exception('Exception occured')
			raise
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

			msg['memories']=dumps(self._memories._get_user_memories(
				profile_user_name=msg['message_author'],
				profile_platform=msg['message_source']))

			msg['knowledge']=dumps(self._knowledge._get_knowledge())

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
		try:
			self._log.info('Calling a Grok LLM for response')
			completion=self._openai.chat.completions.create(
				model=self._config.sicken.model,
				seed=self._config.sicken.seed,
				frequency_penalty=self._config.sicken.frequency_penalty,
				presence_penalty=self._config.sicken.presence_penalty,
				top_p=self._config.sicken.top_p,
				top_logprobs=self._config.sicken.top_logprobs,
				messages=prompt
			)

			self._log.success('Received response')
		   
			resp=completion.choices[0].message.content
			return resp

		except:
			self._log.exception('Exception occured')
			raise

	def _response_request(self, channel, method, properties, body):
		try:
			message=loads(body.decode('utf8'))
			self._log.info('Received response request')


			if not self._model_id and not self._model_name and not self._actions:
				print('Recieved the message request, but the sicken-vtube_plugin didn\'t introduced model and it\'s features. Is the plugin running and does user allowed connection of the plugin?')
				self._log.warning('Recieved the message request, but the sicken-vtube_plugin didn\'t introduced model and it\'s features. Is the plugin running and does user allowed connection of the plugin?')
			
			if message and self._model_id:
				self._log.debug(message)
				response_uuid=str(uuid4())

				prompt=self._build_prompt(msg=message)
				self._log.debug(prompt)

				response=loads(
					self._get_model_response(
						prompt=prompt
					)
				)
				self._log.debug(response)

				self._db.add_chat_message(
					chat_uuid=message['chat_uuid'],
					message_author='Sicken.ai',
					message_source='XAI',
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
				self._log.success('Response request responded successfully')
		except:
			self._log.exception('Exception occured')
			raise	


	def start(self):
		self._introduction_channel.start_consuming()
		


	def stop(self):
		self._response_requests_channel.stop_consuming()


if __name__=="__main__":
	grok_llm=Grok_LLM()
	grok_llm.start()
