from sicken import constants

from adisconfig import adisconfig
from log import Log

from pymongo import MongoClient
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from json import loads
from uuid import uuid4

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class Worker_T5:
	project_name='sicken-worker_t5'

	def __init__(self):
		self.config=adisconfig('/opt/adistools/configs/sicken-worker_t5.yaml')
		self.log=Log(
            parent=self,
            rabbitmq_host=self.config.rabbitmq.host,
            rabbitmq_port=self.config.rabbitmq.port,
            rabbitmq_user=self.config.rabbitmq.user,
            rabbitmq_passwd=self.config.rabbitmq.password,
            debug=self.config.log.debug,
            )

		self.log.info('Initialisation of sicken-worker_t5 started')
		self._init_mongo()
		self._init_rabbitmq()
		self._init_model()
		self._init_tokenizer()
		self.log.success('Initialisation of sicken-worker_t5 succeed')

	def _init_model(self):
		self._t5_model=AutoModelForSeq2SeqLM.from_pretrained(self._get_t5_model(), local_files_only=True)

	def _init_tokenizer(self):
		self._t5_tokenizer=AutoTokenizer.from_pretrained(self._get_t5_tokenizer(), local_files_only=True)

	def _init_mongo(self):
		self._mongo_cli=MongoClient(
			self.config.mongo.host,
			self.config.mongo.port
			)
		self._mongo_db=self._mongo_cli[self.config.mongo.db]


	def _init_rabbitmq(self):
		self._rabbitmq_conn=BlockingConnection(
	        ConnectionParameters(
	            host=self.config.rabbitmq.host,
	            port=self.config.rabbitmq.port,
	            credentials=PlainCredentials(
	                self.config.rabbitmq.user,
	                self.config.rabbitmq.password
	                )
	            )
	        )
		self._rabbitmq_channel=self._rabbitmq_conn.channel()
		self._rabbitmq_channel.basic_consume(
			queue="sicken-requests_t5",
			auto_ack=True,
			on_message_callback=self._callback
			)

	def _get_t5_model(self):
		model=self.config.worker_t5.model
		return constants.Sicken.models_path / "t5" /  model

	def _get_t5_tokenizer(self):
		tokenizer=self.config.worker_t5.tokenizer
		return constants.Sicken.tokenizers_path / "t5" /  tokenizer

	def _get_answer(self, question):
		d=[]
		features=self.t5_tokenizer(question, return_tensors="pt")
		gen_outputs=self.t5_model.generate(features.input_ids, attention_mask=features.attention_mask, max_new_tokens=100000)
		for a in gen_outputs:
			d.append(self.t5_tokenizer.decode(a, skip_special_tokens=True))
		return d

	def _callback(self, channel, method, properties, body):

		msg=body.decode('utf-8')
		msg=loads(msg)

		print(msg)


	def start(self):
		self._rabbitmq_channel.start_consuming()
