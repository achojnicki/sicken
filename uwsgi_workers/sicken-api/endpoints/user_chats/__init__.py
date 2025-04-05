from response import Response

class user_chats:
    def user_chats(self, session_uuid, page=1):
        rsp=Response()

        chats=self._middlewares.chats.get_user_chats(
            session_uuid=session_uuid,
            page=page
            )
        
        rsp.status="Success"
        rsp.message="Chats"
        rsp.data=chats
        return rsp