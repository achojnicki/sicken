from sicken.config import Config

from sicken.log import Log
from sicken.events import events
from sicken.DB import DB
from sicken.exceptions import ChatNotFoundException

from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from pika.adapters.asyncio_connection import AsyncioConnection
from uuid import uuid4
from time import time
from json import loads

from threading import Thread


import asyncio



class Sicken_TikTok_Chat:
	project_name="sicken-TikTok_chat"

	def __init__(self):
		self._active=True
		self._messages={}

		self._config=Config(self)

		self._log=Log(
			parent=self,
			rabbitmq_host=self._config.rabbitmq.host,
			rabbitmq_port=self._config.rabbitmq.port,
			rabbitmq_user=self._config.rabbitmq.user,
			rabbitmq_passwd=self._config.rabbitmq.password,
			debug=self._config.log.debug,
			)


		self._rabbitmq_conn = AsyncioConnection(
			ConnectionParameters(
				host=self._config.rabbitmq.host,
				port=self._config.rabbitmq.port,
				credentials=PlainCredentials(
					self._config.rabbitmq.user,
					self._config.rabbitmq.password
				)
			)
		)

		self._rabbitmq_conn_blocking = BlockingConnection(
			ConnectionParameters(
				host=self._config.rabbitmq.host,
				port=self._config.rabbitmq.port,
				credentials=PlainCredentials(
					self._config.rabbitmq.user,
					self._config.rabbitmq.password
				)
			)
		)


		self._db=DB(self)
		self._events=events(self)


		self._tiktok=TikTokLiveClient(unique_id=self._config.tiktok.channel)

	async def _connect(self):

		self._chat_uuid=str(uuid4())

		self._db.create_chat(
			chat_uuid=self._chat_uuid,
			chat_created=time()
			)

	def _bind(self):
		self._tiktok.add_listener(ConnectEvent, self.on_connect)
		self._tiktok.add_listener(CommentEvent, self.on_comment)


	async def on_connect(self, event: ConnectEvent):
		print(f"Connected to @{event.unique_id} (Room ID: {client.room_id}")


	async def on_comment(self, event: CommentEvent) -> None:
		print(f'{event.user.nickname} said: {event.comment}')
		self._events.event(
			event_name="message_entered",
			event_data={
				"chat_uuid": self._chat_uuid,
				"message_author":  event.user.nickname,
				"message_source": "TikTok",
				"message": event.comment 
				}
		)






		


if __name__=="__main__":
	SickenChat=Sicken_TikTok_Chat()
	SickenChat._bind()
	SickenChat._tiktok.run()



