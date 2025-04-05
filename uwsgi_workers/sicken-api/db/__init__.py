from .users import users
from .sessions import sessions
from .chats import chats



from pymongo import MongoClient

class DB(
    users,
    sessions,
    chats

):
    def __init__(self, root):
        self._root=root

        self.config=self._root.config
        self.log=self._root.log

        self._mongo_cli=MongoClient(
            self.config.mongo.host,
            self.config.mongo.port,
        )

        self._db=self._mongo_cli[self.config.mongo.db]

        self.users=self._db['users']
        self.sessions=self._db['sessions']
        self.chats=self._db['chats']
        self.messages=self._db['messages']
        