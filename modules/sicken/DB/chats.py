class Chats:
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


	def add_chat_message(self, chat_uuid, message_author, message_source, speech=None, gesture=None, func_name=None, call_id=None, tool_calls=None, msg=None):
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

		if func_name:
			message['func_name']=func_name

		if call_id:
			message['call_id']=call_id

		if tool_calls:
			message['tool_calls']=tool_calls

		self._chat_messages_collection.insert_one(message)