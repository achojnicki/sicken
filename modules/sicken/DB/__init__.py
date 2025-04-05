from sicken.exceptions import ChatNotFoundException

from pymongo import MongoClient

class DB:
	def __init__(self, root):
		self._root=root
		self._config=root._config

		self._mongo_cli = MongoClient(
			self._config.mongo.host,
			self._config.mongo.port
		)

		self._mongo_db = self._mongo_cli[self._config.mongo.db]
		self._chats_collection=self._mongo_db['chats']

		self._chat_messages_collection=self._mongo_db['chat_messages']

	def get_chats(self):
		query={}
		return self._chats_collection.find_one(query)

	def create_chat(self, chat_uuid, chat_created):
		document={
			"chat_uuid": str(chat_uuid),
			"chat_created": chat_created
		}
			
		self._chats_collection.insert_one(document)

	def get_chat(self, chat_uuid):
		query={'chat_uuid': chat_uuid}
		return self._chats_collection.find_one(query)

	def get_chat_messages(self, chat_uuid):
		if not self.get_chat(chat_uuid):
			raise ChatNotFoundException

		messages=[]

		query={'chat_uuid': chat_uuid}
		cursor=self._chat_messages_collection.find(query)

		for message in cursor:
			del message['_id']
			messages.append(message)

		return messages


	def add_chat_message(self, chat_uuid, message_author, message_source, speech=None, gesture=None, msg=None):
		if not self.get_chat(chat_uuid):
			raise ChatNotFoundException

		message={
			"chat_uuid": str(chat_uuid),
			"message_author": message_author,
			"message_source": message_source,
		}

		if speech:
			message['speech']=speech

		if gesture:
			message['gesture']=gesture

		if msg:
			message['message']=msg

		self._chat_messages_collection.insert_one(message)

