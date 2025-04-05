from .auth import Auth
from .chats import Chats

class Middlewares:
	def __init__(self, root):
		self._root=root

		self.auth=Auth(root)
		self.chats=Chats(root)
