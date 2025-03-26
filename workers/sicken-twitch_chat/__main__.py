from adistools.adisconfig import adisconfig

from sicken.log import Log
from sicken.events import events
from sicken.DB import DB
from sicken.exceptions import ChatNotFoundException

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from pika.adapters.asyncio_connection import AsyncioConnection
from uuid import uuid4
from time import time
from json import loads

from threading import Thread


import asyncio

USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

class Sicken_Twitch_Chat:
	project_name="sicken-twitch_chat"

	def __init__(self):
		self._active=True
		self._messages={}

		self._config=adisconfig('/opt/sicken/configs/sicken-twitch_chat.yaml')

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

		self._incoming_messages_channel = self._rabbitmq_conn_blocking.channel()
		self._incoming_messages_channel.basic_consume(
			queue='sicken-twitch_responses',
			auto_ack=True,
			on_message_callback=self._message
		)


		self._db=DB(self)
		self._events=events(self)


		self._chat_uuid=None

	def _start_thread(self):
		t=Thread(target=self._incoming_messages_channel.start_consuming, args=[])
		t.daemon=True
		t.start()


	def _message(self, channel, method, properties, body):
		message=loads(body.decode('utf8'))
		print(message)
		if message and message['speech'] and hasattr(self, '_chat'):
			self._messages[message['response_uuid']]=message



	async def _send_message(self, message):
		if hasattr(self, "_chat"):
			print('wykonało w async')
			await self._chat.send_message(self._config.twitch.channel, message)

	async def _connect(self):
		self._loop=asyncio.get_running_loop()

		self._twitch = await Twitch(self._config.twitch.client_id, self._config.twitch.secret_key)
		self._auth = UserAuthenticator(self._twitch, USER_SCOPE)
		self._token, self._refresh_token = await self._auth.authenticate()
		await self._twitch.set_user_authentication(self._token, USER_SCOPE, self._refresh_token)

		self._chat = await Chat(self._twitch)

	async def _bind(self):
		self._chat.register_event(ChatEvent.READY, self.on_ready)
		# listen to chat messages
		self._chat.register_event(ChatEvent.MESSAGE, self.on_message)
		# listen to channel subscriptions
		self._chat.register_event(ChatEvent.SUB, self.on_sub)

		#chat.register_command('reply', test_command)


	async def on_ready(self, ready_event: EventData):
		self._chat_uuid=str(uuid4())

		self._db.create_chat(
			chat_uuid=self._chat_uuid,
			chat_created=time()
			)
		print('Bot is ready for work, joining channels')
		await ready_event.chat.join_room(self._config.twitch.channel)


	async def on_message(self, msg: ChatMessage):
		print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
		if msg.user.name!=self._config.twitch.channel:
			self._events.event(
				event_name="message_entered",
				event_data={
					"chat_uuid": self._chat_uuid,
					"message_author":  msg.user.name,
					"message_source": "Twitch",
					"message": msg.text 
					}
			)



	async def on_sub(self, sub: ChatSub):
		print(f'New subscription in {sub.room.name}:\n',
			f'  Type: {sub.sub_plan}\n',
			f'  Message: {sub.sub_message}')


	async def test_command(self, cmd: ChatCommand):
		if len(cmd.parameter) == 0:
			await cmd.reply('you did not tell me what to reply with')
		else:
			await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')


	async def run(self):
		await self._connect()
		await self._bind()
		self._chat.start()
		try:
			while self._active:
				for message in dict(self._messages):
					print(message, self._messages[message])
					await self._send_message(self._messages[message]['speech'])
					del self._messages[message]

				await asyncio.sleep(0.1)

		finally:
			self._chat.stop()
			await self._twitch.close()



if __name__=="__main__":
	SickenChat=Sicken_Twitch_Chat()
	SickenChat._start_thread()
	asyncio.run(SickenChat.run())


