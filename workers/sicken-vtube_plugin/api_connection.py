from websockets.sync.client import connect
from json import dumps, loads
from pprint import pprint


class API_Connection:
	def __init__(self, root):
		self.root=root

		self.log=root.log

		self.connection=None
		self.connection_string=None

	def connect(self, conection_string):
		self.connection_string=conection_string
		self.connection=connect(conection_string)

	def send(self, data):
		self.connection.send(dumps(data))

	def send_and_recv(self, data):
		self.send(data)
		data=self.connection.recv()
		data=loads(data)
		pprint(data)
		return data