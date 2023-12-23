from sicken import constants
from adisconfig import adisconfig
from log import Log
from pymongo import MongoClient
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from json import loads, dumps
from uuid import uuid4
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class Worker_T5:
	project_name='sicken-worker_t5_chat'

	def __init__(self):
		self.config=adisconfig('/opt/adistools/configs/sicken-worker_t5_chat.yaml')
		self.log=Log(
            parent=self,
            rabbitmq_host=self.config.rabbitmq.host,
            rabbitmq_port=self.config.rabbitmq.port,
            rabbitmq_user=self.config.rabbitmq.user,
            rabbitmq_passwd=self.config.rabbitmq.password,
            debug=self.config.log.debug,
            )

		self.log.info('Initialisation of sicken-worker_t5_chat started')
		self._init_mongo()
		self._init_rabbitmq()
		self._init_model()
		self._init_tokenizer()
		self.log.success('Initialisation of sicken-worker_t5_chat succeed')

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
			queue="sicken-requests_t5_chat",
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
		features=self._t5_tokenizer(question, return_tensors="pt")
		gen_outputs=self._t5_model.generate(
			features.input_ids,
			attention_mask=features.attention_mask,
			#max_new_tokens=100000,
			num_beams=16,
			min_length=80,
			max_length=1000,
			temperature=0.76,
			do_sample=True,
			early_stopping= True,
			no_repeat_ngram_size=2,
			length_penalty=2
			)
		return self._t5_tokenizer.decode(gen_outputs[0], skip_special_tokens=True)

	def _build_response_message(self, user_uuid, chat_uuid, socketio_session_id, message):
		return dumps({
			"user_uuid": user_uuid,
			"chat_uuid": chat_uuid,
			"socketio_session_id": socketio_session_id,
			"message": message
		})


	def _callback(self, channel, method, properties, body):
		msg=body.decode('utf-8')
		msg=loads(msg)
		response=self._get_answer(msg['message'])

		msg=self._build_response_message(
			user_uuid="95a952c4-0deb-4382-9a51-1932c31c9bc0",
			chat_uuid=msg['chat_uuid'],
			socketio_session_id=msg['socketio_session_id'],
			message=response)

		self._rabbitmq_channel.basic_publish(
			exchange="",
			routing_key="sicken-responses_chat",
			body=msg)


	def start(self):
		self._rabbitmq_channel.start_consuming()


if __name__=="__main__":
	worker_t5=Worker_T5()
	worker_t5.start()