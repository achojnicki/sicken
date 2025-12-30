from adisconfig import adisconfig
from adislog import adislog

from threading import Thread, Event, Lock
from time import sleep
from subprocess import Popen, PIPE
from os import getpid, kill, read, write, close
from signal import SIGTERM
from select import select
from platform import system


import socketio
import socket
import pyte
if system()=='Linux' or system()=='Darwin':
	import pty

SOCKETIO_URL='ws://{server_addr}:{server_port}/socket.io/'


class sicken_agent:
	def __init__(self, ):
		self._active=True

		self._config=adisconfig('config.yaml')
		self._log=adislog(
			project_name='sicken-agent',
			backends=['terminal_colorful'],
			debug=False
			)

		self._socketio=socketio.Client(logger=False, engineio_logger=False)
		self._socketio.on('command_request', namespace="/", handler=self._execute_command)
		self._socketio.on('spawn_process_request', namespace="/", handler=self.spawn_process)
		self._socketio.on('terminal_snapshot_request', namespace="/", handler=self.process_terminal_snapshot_request)
		self._socketio.on('terminal_characters_request', namespace="/", handler=self.terminal_characters)


		self._processes={}
		self._processes_lock=Lock()


	def spawn_process(self, data):
		self._log.info(f'Spawning new process. process_uuid: {data["process_uuid"]}, command: {data["command"]}')
		self._spawn_process(
			process_uuid=data['process_uuid'],
			cmd=data['command']
			)

	def _spawn_process(self,process_uuid, cmd):
		master_fd, slave_fd = pty.openpty()

		terminal=pyte.Screen(self._config.terminal.cols, self._config.terminal.rows)
		stream=pyte.Stream(terminal)

		process=Popen(
		    [cmd],
		    env={
		    	"TERM": "vt100",
		    	"COLUMNS": str(self._config.terminal.cols),
		    	"LINES": str(self._config.terminal.rows),
		    	"HOME": "/home/sicken",
		    	"PATH": "/bin:/usr/bin:/usr/local/bin"
		    },
		    shell=True,
		    stdin=slave_fd,
		    stdout=slave_fd,
		    stderr=slave_fd,
		    close_fds=True,
		)

		close(slave_fd)

		stdout_lock=Lock()


		with self._processes_lock:
			self._processes[process_uuid]={
				"process_uuid": process_uuid,
				"command": cmd,
				"process": process,
				"pty_master_fd": master_fd,
				"pty_slave_fd": slave_fd,
				"terminal": terminal,
				"terminal_stream": stream,
				"terminal_lock": stdout_lock,
				"status": "Running",
				"exit_code": False
			}


	def _terminal_updater_thread(self):
		while True:
			for process_uuid in dict(self._processes):
				process=self._processes[process_uuid]

				with process['terminal_lock']:
					r, _, _ = select([process['pty_master_fd']], [], [], 0.1)

					if process['pty_master_fd'] in r:
						try:
							data=read(process['pty_master_fd'], 4096)
							if not data:
								continue

							process['terminal_stream'].feed(data.decode(errors='ignore'))
						except OSError:
							if process['process'].poll()!=None:

								process['status']="Exited"
								process['exit_code']=process['process'].returncode

			sleep(0.01)
	
	def terminal_characters(self, data):
		process_uuid=data['process_uuid']
		characters_string=data['characters_string']

		self._send_string(process_uuid, characters_string)


	def _send_string(self, process_uuid, characters_string):
		if process_uuid in self._processes:
			process=self._processes[process_uuid]
			characters_string=characters_string.encode('utf-8')
			with process['terminal_lock']:
				write(process['pty_master_fd'], characters_string)


	def process_terminal_snapshot_request(self, data):
		process=self._processes[data['process_uuid']]
		snapshot=self._screen_snapshot(data['process_uuid'])

		self._log.info(f'Sicken requested a snapshot of the terminal. process_uuid: {process["process_uuid"]}')
		self._socketio.emit(
			'terminal_snapshot_response',
			{
				"process_uuid": process['process_uuid'],
				"command": process['command'],
				"terminal_snapshot": snapshot,
				"status": process['status'],
				"exit_code": process['exit_code']
			},
			namespace="/")

	def _screen_snapshot(self, process_uuid):
		process=self._processes[process_uuid]

		with process['terminal_lock']:
			return process['terminal'].display

	def connect(self):
		self._log.info(f'Connecting to the agent server at:{SOCKETIO_URL.format(server_addr=self._config.sicken_agent.server_addr,server_port=self._config.sicken_agent.server_port)}')
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
		t.daemon=True
		t.start()

	def terminal_updater_thread(self):
		t=Thread(target=self._terminal_updater_thread, args=())
		t.daemon=True
		t.start()

	def start(self):
		self.terminal_updater_thread()
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
		self._log.info(f'Execution request received. command_uuid: {command_uuid}, cmd: {cmd} ')
		stdout, stderr=p.communicate()
		exit_code=p.returncode
		if exit_code==0:
			self._log.success(f"Execution of command succeeded. exit_code: {exit_code}, stdout: {stdout}, stderr: {stderr}")
		else:
			self._log.warning(f"A non-zero exit code: {exit_code}. exit_code: {exit_code}, stdout: {stdout}, stderr: {stderr}")

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