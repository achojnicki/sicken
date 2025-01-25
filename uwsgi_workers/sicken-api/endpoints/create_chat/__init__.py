from response import Response

class create_chat:
    def create_chat(self, session_uuid):
        rsp=Response()
        chat=self._middlewares.chats.create_chat(
            session_uuid=session_uuid
        )
    
        rsp.status='Success'
        rsp.message='Chat created'
        rsp.data=chat
        
        return rsp