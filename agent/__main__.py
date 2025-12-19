from adisconfig import adisconfig
from adislog import adislog

from threading import Thread, Event, Lock
import socketio
from time import sleep
from subprocess import Popen, PIPE
from os import getpid, kill
from signal import SIGTERM


import socket

SOCKETIO_URL='ws://{server_addr}:{server_port}/socket.io/'



class sicken_agent:
	def __init__(self, ):
		self._active=True

		self._config=adisconfig('config.yaml')
		self._log=adislog(
			project_name='sicken-agent',
			backends=['terminal_colorful'],
			debug=True
			)

		self._socketio=socketio.Client(logger=False, engineio_logger=False)
		self._socketio.on('command_request', namespace="/", handler=self._execute_command)

	def connect(self):
		self._log.info('Connecting to the agent server at:', SOCKETIO_URL.format(
			server_addr=self._config.sicken_agent.server_addr,
			server_port=self._config.sicken_agent.server_port)
		)
		self._socketio.connect(
			SOCKETIO_URL.format(
				server_addr=self._config.sicken_agent.server_addr,
				server_port=self._config.sicken_agent.server_port), 
			wait_timeout=60, 
			retry=True
			)
		self._socketio.emit('agent_connect')
		self._log.success('Connected to the server')

	def _ping(self):
		e=Event()
		while self._active:
			self._log.debug('Pinging server')
			try:
				self._socketio.emit('agent_ping')
			except:
				self._log.info('Disconnected from server. Exitting...')
				kill(getpid(), SIGTERM)
			e.wait(timeout=1)

	def ping(self):
		t=Thread(target=self._ping, args=())
		t.start()

	def start(self):
		self.connect()
		self.ping()
		self._socketio.wait()

	def _execute_command(self, data):
		command_uuid=data['command_uuid']
		cmd=data['command']
		p=Popen(
                cmd,
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                )
		self._log.info('Execution request received')
		self._log.info(f"command_uuid: {command_uuid}")
		self._log.info(f'cmd: {cmd}')
		stdout, stderr=p.communicate()
		exit_code=p.returncode
		if exit_code==0:
			self._log.success(f"exit_code: {exit_code}")
		else:
			self._log.warning(f"exit_code: {exit_code}")
		self._log.info(f"stdout: {stdout}")
		self._log.info(f"stderr: {stderr}")

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