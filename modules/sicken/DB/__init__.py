from sicken.DB.chats import Chats
from sicken.DB.classifications import Classifications
from sicken.DB.profiles import Profiles
from sicken.DB.memories import Memories
from sicken.DB.knowledge import Knowledge

from sicken.exceptions import ChatNotFoundException

from pymongo import MongoClient

class DB(Chats, Classifications, Profiles, Memories, Knowledge):
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

		self._classification_definitions_collection=self._mongo_db['classification_definitions']
		self._classification_groups_collection=self._mongo_db['classification_groups']
		self._user_profiles_collection=self._mongo_db['profiles']
		self._memories_collection=self._mongo_db['memories']


		self._knowledge_collection=self._mongo_db['knowledge']
		self._knowledge_groups_collection=self._mongo_db['knowledge_groups']