from endpoints import (
    login,
    logout,
    create_chat,
    user_chats,
    user_chat
    )

class Endpoints(login.login,
    logout.logout,
    create_chat.create_chat,
    user_chats.user_chats,
    user_chat.user_chat
    ):
    def __init__(self, root):
        self._root=root

        self._middlewares=root.middlewares
        self._log_handle=root.log_handle

        self._endpoints_with_required_login=[
            self.logout,
            self.create_chat,
            self.user_chats,
            self.user_chat
            ]