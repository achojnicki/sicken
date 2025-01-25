from response import Response

class user_chat:
    def user_chat(self, chat_uuid,  session_uuid):
        rsp=Response()

        chat=self._middlewares.chats.get_user_chat(
            session_uuid=session_uuid,
            chat_uuid=chat_uuid
            )
        
        rsp.status="Success"
        rsp.message="Chat"
        rsp.data=chat
        return rsp