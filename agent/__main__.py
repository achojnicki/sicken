from threading import Thread, Event, Lock
import socketio
from time import sleep
from subprocess import Popen, PIPE


import socket

SOCKETIO_URL='ws://localhost:9999/socket.io/'



class sicken_agent:
	def __init__(self, ):
		self._active=True


		self._socketio=socketio.Client(logger=False, engineio_logger=False)

		
		self._socketio.on('command_request', namespace="/", handler=self._execute_command)

	def connect(self):
		self._socketio.connect(SOCKETIO_URL, wait_timeout=60, retry=True)
		self._socketio.emit('agent_connect')

	def _ping(self):
		e=Event()
		while self._active:
			print('ping')
			self._socketio.emit('agent_ping')
			e.wait(timeout=1)

	def ping(self):
		t=Thread(target=self._ping, args=())
		t.start()

	def start(self):
		self.connect()
		self.ping()
		#self._socketio.wait()

	def _execute_command(self, data):
		command_uuid=data['command_uuid']
		cmd=data['command']
		p=Popen(
                cmd,
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                )
		print('execution request')
		print(f"command_uuid: {command_uuid}")
		print(f'cmd: {cmd}')
		stdout, stderr=p.communicate()
		exit_code=p.returncode
		print(f"exit_code: {exit_code}")
		print(f"stdout: {stdout}")
		print(f"stderr: {stderr}")

		self._socketio.emit(
			'command_response',
			{
				"command_uuid": command_uuid,
				"command": cmd,
				"exit_code":exit_code,
				"stdout":stdout.decode('utf-8'),
				"stderr":stderr.decode('utf-8'),
			},
			namespace="/")



if __name__=="__main__":
	app=sicken_agent()
	app.start()