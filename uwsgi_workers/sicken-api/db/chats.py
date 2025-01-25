class chats:
    def create_chat(self, chat_uuid: str, user_uuid: str):
        document={
            "chat_uuid": str(chat_uuid),
            "user_uuid": str(user_uuid),
            "chat_title": None
            }
        self.chats.insert_one(document)
        return document

    def get_chats(self, limit, skip):
        chats=[]
        cursor=self.chats.find().skip(skip).limit(limit)
        for item in cursor:
            chats.append(item)
        return chats

    def get_chats_by_user_uuid(self, user_uuid, limit, skip):
        query={
            "user_uuid":user_uuid
        }

        chats=[]
        cursor=self.chats.find(query).skip(skip).limit(limit)
        for item in cursor:
            chats.append(item)
        return chats


    def get_user_chat(self, chat_uuid: str, user_uuid: str):
        query={
            "chat_uuid": chat_uuid,
            "user_uuid": user_uuid
            }

        chat={}
        cursor=self.chats.find_one(query)
        for item in cursor:
            chat[item]=cursor[item]

        return chat

    def get_chat_messages_by_chat_uuid(self, chat_uuid:str):
        query={
            "chat_uuid": chat_uuid,
            }

        messages=[]
        cursor=self.messages.find_one(query)

        for item in cursor:
            messages.append(item)

        return messages

    def get_chat_message_by_message_uuid(self, message_uuid:str):
        query={
            'message_uuid': message_uuid
        }
        message=self.messages.find_one(query)
        del message['_id']
        return message

    def add_chat_message(self, chat_uuid:str, user_uuid:str, message_content:str):
        document={
            'chat_uuid': chat_uuid,
            'user_uuid': user_uuid,
            'message_uuid': message_uuid,
            'message_content': message_content
        }
        self.messages.insert_one(document)
        del document['_id']
        return document
