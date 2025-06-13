from sicken.config import Config

from sicken.log import Log
from sicken.events import events
from sicken.DB import DB
from sicken.exceptions import ChatNotFoundException
from sicken.memories import Memories

from constants import SYSTEM_MESSAGE

from openai import OpenAI
from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from json import loads, dumps
from pprint import pprint
from pathlib import Path
from uuid import uuid4
from time import time



class Classification:
	project_name="sicken-classification"

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

		self._classification_requests_channel = self._rabbitmq_conn.channel()
		self._classification_requests_channel.basic_consume(
			queue='sicken-classification_requests',
			auto_ack=True,
			on_message_callback=self._classification_request
		)
		
		self._openai=OpenAI(api_key=self._config.openai.api_key)
		self._db=DB(self)
		self._events=events(self)

		self._memories=Memories(self)
		
		self._classifications=dumps(self._db.get_classifications())



	def _build_prompt(self, msg):
		try:
			prompt=[]
			prompt.append(
				{"role": "system", "content": SYSTEM_MESSAGE.replace('<!_categories_!>', self._classifications)}
				)
			prompt.append({"role": "user", "content": dumps(msg)})

			return prompt
		except:
			self._log.exception('Exception ocured in the build_prompt')
			raise


	def _get_model_response(self, prompt):
		try:
			self._log.info('Calling an OpenAi LLM for classification')
			completion=self._openai.chat.completions.create(
				model=self._config.sicken.model,
				seed=self._config.sicken.seed,
				messages=prompt
			)

			self._log.success('Received response')
			resp=completion.choices[0].message.content
			return resp

		except:
			self._log.exception('Exception occured')
			raise

	def _classification_request(self, channel, method, properties, body):
		try:
			self._log.info('Received classification request')
			message=loads(body.decode('utf8'))

			if message:
				print('Queue message:')
				print(message)
				self._log.debug(message)
				response_uuid=str(uuid4())

				prompt=self._build_prompt(msg=message)
				print('Prompt:')
				print(prompt)
				self._log.debug(prompt)


				response=self._get_model_response(
						prompt=prompt
					)
				print('Model response:')
				print(response)
				response=loads(response)
				self._log.debug(response)

				self._log.info(f'OpenAI LLM found {len(response["classifications"])} classification{"s" if len(response["classifications"])>1 else ""} in the message.')
				for classification in response['classifications']:
					self._memories._add_memory(
						profile_user_name=message['profile_user_name'],
						profile_platform=message['profile_platform'],
						classification_uuid=classification['classification_uuid'],
						memory_value=classification['memory_value'],
						sickens_comment=classification['sickens_comment']
						)

				if len(response['classifications'])>0:
					self._log.success('Memories saved.')
		except:
			self._log.exception('Exception occured')
			raise

	def start(self):
		self._classification_requests_channel.start_consuming()
		


	def stop(self):
		self._classification_requests_channel.stop_consuming()


if __name__=="__main__":
	classification=Classification()
	classification.start()
