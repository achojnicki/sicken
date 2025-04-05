from uuid import uuid4

class Chats:
    def __init__(self, root):
        self._root=root

        self.config=self._root.config
        self.log=self._root.log
        self.db=self._root.db

    def create_chat(self, session_uuid: str):
        user_uuid=self.db.get_session_by_session_uuid(session_uuid)['user_uuid']
        chat_uuid=uuid4()

        data=self.db.create_chat(
            chat_uuid=chat_uuid,
            user_uuid=user_uuid
            )
        del data['_id']

        chat={str(chat_uuid):data}
        self.log.success("Created chat successfully")
        return chat

    def get_user_chats(self, session_uuid:str, page=1):
        limit=self.config.api.results_per_page
        skip=(int(page)-1)*limit
        user_uuid=self.db.get_session_by_session_uuid(session_uuid)['user_uuid']

        data=self.db.get_chats_by_user_uuid(
            limit=limit,
            skip=skip,
            user_uuid=user_uuid
            )
        for item in data:
            del item['_id']

        chats={}
        for chat in data:
            chats[chat['chat_uuid']]=chat


        self.log.success("Obtained list of user's chats.")
        return chats

    def get_user_chat(self, session_uuid: str, chat_uuid:str):
        user_uuid=self.db.get_session_by_session_uuid(session_uuid)['user_uuid']
        data=self.db.get_user_chat(
            user_uuid=user_uuid,
            chat_uuid=chat_uuid
            )
        del data['_id']
        chat={chat_uuid:data}
        self.log.success('Obtained details about a short URL')
        return url

    def add_chat_message(self, session_uuid:str, chat_uuid: str, message_content:str ):
        message_uuid=uuid4()
        document={
            "chat_uuid": chat_uuid,
            "message_uuid": message_uuid,
            "message_content": message_content,
            "user_uuid": user_uuid

        }

        self.db.add_chat_message(document)
