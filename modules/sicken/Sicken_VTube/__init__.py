from websockets.sync.client import connect
from random import randint
from json import dumps, loads
from pprint import pprint
from base64 import b64encode
from time import time, sleep
from math import ceil
from pprint import pprint
from random import randint
import numpy as np

SICKEN_IMAGE="Sicken.jpg"
PLUGIN_NAME="Sicken.ai"
PLUGIN_DEVELOPER="adrianchojnicki.me"

FRAME=0.035


class message_builder:
	def __init__(self, root):
		self._root=root

		self._auth_token=None

	@property
	def auth_token(self):
		return self._auth_token

	@auth_token.setter
	def auth_token(self, auth_token):
		self._auth_token=auth_token

	@property
	def _sicken_image(self):
		with open(SICKEN_IMAGE, 'rb') as sicken_img:
			return b64encode(sicken_img.read()).decode('utf-8')

	def pre_auth_message(self, request_id):
		return dumps(
			{
				"apiName": "VTubeStudioPublicAPI",
				"apiVersion": "1.0",
				"requestID": request_id,
				"messageType": "AuthenticationTokenRequest",
				"data": {
					"pluginName": PLUGIN_NAME,
					"pluginDeveloper": PLUGIN_DEVELOPER,
					"pluginIcon": self._sicken_image
				}
			}
		)

	def auth_message(self, request_id):
		return dumps(
			{
				"apiName": "VTubeStudioPublicAPI",
				"apiVersion": "1.0",
				"requestID": "SomeID",
				"messageType": "AuthenticationRequest",
				"data": {
					"pluginName": PLUGIN_NAME,
					"pluginDeveloper": PLUGIN_DEVELOPER,
					"authenticationToken": self._auth_token
				}
			}
		)

	def load_model_message(self, request_id, model_id):
		print('auth_token:',self._auth_token)
		return dumps(
			{
				"apiName": "VTubeStudioPublicAPI",
				"apiVersion": "1.0",
				"requestID": request_id,
				"messageType": "ModelLoadRequest",
				"data": {
					"authenticationToken": self._auth_token,
					"modelID": model_id
				}
			}
		)

	def _add_custom_parameter(self, request_id, parameter_name, val_min, val_max, default):
		return dumps(
			{
				"apiName": "VTubeStudioPublicAPI",
				"apiVersion": "1.0",
				"requestID": request_id,
				"messageType": "ParameterCreationRequest",
				"data": {
					"parameterName": parameter_name,
					"min": val_min,
					"max": val_max,
					"defaultValue": default
				}
			})


	def _format_parameters(self, parameters):
		data=[]
		for parameter in parameters:
			data.append({
				"id": parameter,
				"value": parameters[parameter]
				})
		return data

	def _set_model_parameters_message(self, request_id, model_id, parameters:dict):
		return dumps(
			{
				"apiName": "VTubeStudioPublicAPI",
				"apiVersion": "1.0",
				"requestID": request_id,
				"messageType": "InjectParameterDataRequest",
				"data": {
					"mode": "set",
					"modelID": model_id,
					"parameterValues": self._format_parameters(parameters)
				}
			}
		)


class SickenException(Exception):
	pass

class ModelException(SickenException):
	pass

class APIConnectionException(SickenException):
	pass


class RequestIdDoNotMatch(APIConnectionException):
	pass


class ModelNotLoadedException(ModelException):
	pass


class _API_Connectyion_Auth:
	@property
	def authenticated(self):
		return True if self._auth_token else False

	@property
	def auth_token(self):
		return self._auth_token

	def auth(self):
		request_id=self._generate_request_id()

		resp=self._request_response(
			request_data=self._message_builder.pre_auth_message(
				request_id=request_id
				)
			)

		if resp['requestID']!=request_id:
			raise RequestIdDoNotMatch

		self._message_builder.auth_token=resp['data']['authenticationToken']
		self._auth_token=resp['data']['authenticationToken']

		request_id=self._generate_request_id()

		resp=self._request_response(
			request_data=self._message_builder.auth_message(
				request_id=request_id
				)
			)


class _API_Connection_Model:
	def load_model(self, model_id):
		request_id=self._generate_request_id()

		resp=self._request_response(
			request_data=self._message_builder.load_model_message(
				request_id=request_id,
				model_id=model_id
				)
			)
		if resp['requestID']!=request_id:
			raise RequestIdDoNotMatch

		model_id=resp['data']['modelID']

		return model_id

	def set_model_parameters(self, model_id, parameters):
		request_id=self._generate_request_id()
		resp=self._request_response(
				request_data=self._message_builder._set_model_parameters_message(
					request_id=request_id,
					model_id=model_id,
					parameters=parameters
					)
				)
	def add_custom_parameter(self, model_id, parameter_name, val_min, val_max, default):
		request_id=self._generate_request_id()
		resp=self._request_response(
				request_data=self._message_builder._add_custom_parameter(
					request_id=request_id,
					parameter_name=parameter_name,
					val_min=val_min,
					val_max=val_max,
					default=default
				)
			)



class API_Connection(
	_API_Connectyion_Auth,
	_API_Connection_Model):
	def __init__(self, root):
		self._root=root
		self._message_builder=message_builder(root)

		self._connection=None

		self._auth_token=None




	def _generate_request_id(self):
		request_id=""
		for char in range(32):
			request_id+=chr(randint(97, 122))

		return request_id

	def _request_response(self, request_data):
		#pprint(loads(request_data))
		t=time()
		self._connection.send(request_data)
		msg=loads(self._connection.recv())
		#print(time()-t)
		#pprint(msg)
		#print('---')
		return msg

	def init_connection(self, host, port):
		self._connect(host=host, port=port)
		self.auth()

	def _connect(self, host, port):
		self._connection=connect(f"ws://{host}:{port}")


MOUTH_LETTERS_MOUTH_OPEN={
	"a": 35,
	"o": 30,
	"e": 32,
	"u": 5,
	"h": 10,
	"u": 18,
	"i": 15,
	"w": 8,
	"y": 20,
	"n": 3,
	"p": 0,
	"b": 0,
	"m": 0,
	"t": 10,
	"l": 5,
	"w": 5,
	"f": 7,
	"s": 25,
	'h': 15,
	'j': 14,
	'd': 15,
	'g': 20,
	'l': 10,
	'c': 15,
	'r': 7
	
}


class Animation_Seq:
	def __init__(self):
		self._actions={}
		self._sequence={}
		self._words=[]

		self._duration=0.0

	def _generate_wink_range(self, start, stop, step):
		l=list(range(start,stop-(step*2),-step))+list(range(stop, start+step,step))
		return l

	def generate_possessed_look_range(self, start, stop, step):
		l=list(range(start,stop,-step))

		x=ceil(int(self._duration/FRAME))
		for _ in range(x):
			l.append(stop)

		l=l+list(range(stop,start+(2*step),step))
		return l

	def _generate_angry_range(self, start, stop, step):
		l=list(range(start,stop+(step*2),step))

		x=ceil(int(self._duration/FRAME))
		for _ in range(x):
			l.append(stop)

		l.append(start)
		return l

	def _generate_shock_range(self, start, stop, step):
		l=list(range(start,stop,step))

		x=ceil(int(self._duration/FRAME))
		for _ in range(x):
			l.append(stop)

		l=l+list(range(stop,start,-step))
		l.append(start)
		return l

	def _generate_shock_sign_range(self, start, stop, step):
		l=list(range(start,stop+(step*2),step))

		return l

	def _generate_tilt_left_range(self, start, stop, step):
		l=list(range(start,stop+step,step))+list(range(stop, start-step,-step))+[0]
		return l

	def _generate_tilt_right_range(self, start, stop, step):
		l=list(range(start, stop+step,-step))+list(range(stop,start+step,step))+[0]
		return l

	def _generate_nod_range(self, start, stop, step):
		return list(range(start, stop, step))+list(range(stop, -stop, -step))+list(range(-stop, start, step))+[0]

	def _generate_speak_range_mouth_open(self, words):
		seq=[]
		for word_index in range(0,len(words)):
			frame=0.035
			print(words[word_index]['word'])
			start=words[word_index]['start']
			end=words[word_index]['end']
			duration=end-start
			word_len=len(words[word_index]['word'])

			print(f'start: {start}, end: {end}, duration: {duration}, word_len: {word_len}')
			for letter in words[word_index]['word']:
				iters=(duration/word_len)/frame
				
				if letter.lower() in MOUTH_LETTERS_MOUTH_OPEN:
					if iters>1:
						path=np.linspace(
							seq[-1] if len(seq)>0 else 0,
							MOUTH_LETTERS_MOUTH_OPEN[letter.lower()],
							ceil(iters)
						)
					else:
						path=[MOUTH_LETTERS_MOUTH_OPEN[letter.lower()]]
					print(f'path: {path}')

					for repeat in range(0,ceil(iters)):
						seq.append(int(path[repeat]))

				else:
					for repeats in range(0,ceil(iters)):
						seq.append(seq[-1])

				print(f'\tletter: {letter} iters: {iters}, seq[-1]:{seq[-1]}')

			if (len(words)-1)>word_index:
				pause_duration=words[word_index+1]['start']-words[word_index]['end']
				print(f"pause_duration: {pause_duration}")
				if pause_duration>frame:
					iters=pause_duration*frame
					print(f'\titers" {iters}')
					for repeats in range(0, ceil(iters)):
						seq.append(0)

		seq.append(0)
		return seq


	def add_action(self, action):
		print(action)
		self._actions[action['action_name']]=action


	@property
	def sequence(self):
		if 'speak' in self._actions:
			self._duration=self._actions['speak']['duration']

			ra=self._generate_speak_range_mouth_open(self._actions['speak']['words'])
			self._sequence['speak']={'MouthOpen': ra}

		else:
			self._duration=1.0

		for action in self._actions:
			if action=='nod_yes':
				ra=self._generate_nod_range(0,30,4)

				self._sequence[self._actions[action]['action_name']]={'FaceAngleY': ra}
			elif action=='blink':
				l=self._generate_wink_range(100,0,40)
				self._sequence[self._actions[action]['action_name']]={'EyeOpenRight': l, 'EyeOpenLeft': l}

			elif action=='nod_no':
				ra=self._generate_nod_range(0,30,4)

				self._sequence[self._actions[action]['action_name']]={'FaceAngleX': ra}

			elif action=='wink_left_eye':
				ra=self._generate_wink_range(100, 0, 20)

				self._sequence[self._actions[action]['action_name']]={'EyeOpenLeft': ra,}

			elif action=='wink_left_eye_tilt':
				ra=self._generate_wink_range(100, 0, 20)
				ti=self._generate_tilt_left_range(0, 1500, 200)

				self._sequence[self._actions[action]['action_name']]={'EyeOpenLeft': ra, "FaceAngleZ": ti}

			elif action=='wink_right_eye':
				ra=self._generate_wink_range(100, 0, 20)
				self._sequence[self._actions[action]['action_name']]={'EyeOpenRight': ra}

			elif action=='wink_right_eye_tilt':
				ra=self._generate_wink_range(100, 0, 20)
				ti=self._generate_tilt_right_range(0, -1500, 200)

				self._sequence[self._actions[action]['action_name']]={'EyeOpenRight': ra, "FaceAngleZ": ti}

			elif action=='tilt_head_left':
				ti=self._generate_tilt_left_range(0, 1500, 200)

				self._sequence[self._actions[action]['action_name']]={"FaceAngleZ": ti}

			elif action=='tilt_head_right':
				ti=self._generate_tilt_right_range(0, -1500, 200)

				self._sequence[self._actions[action]['action_name']]={"FaceAngleZ": ti}

			elif action=='angry_sign':
				ra=self._generate_angry_range(0, 100, 40)

				self._sequence[self._actions[action]['action_name']]={"FaceAngry": ra}

			elif action=='shock_sign':
				ra=self._generate_shock_sign_range(0, 100, 40)

				self._sequence[self._actions[action]['action_name']]={"ShockSign": ra}

			elif action=='shock':
				ra=self._generate_shock_range(0, 80, 10)

				self._sequence[self._actions[action]['action_name']]={"Shock": ra}

			elif action=='posessed_look':
				ra=self.generate_possessed_look_range(100,0,10)

				self._sequence[self._actions[action]['action_name']]={"PosessedLook": ra}

		return self._sequence


class Models:
	def __init__(self, root):
		self._root=root

		self._models=[]
		self._api_connection=self._root._api_connection

		self._actions={}
		self._processed_actions=[]

	def load_model(self, model_id):
		model_id=self._api_connection.load_model(model_id)
		self._models.append(model_id)

		self._api_connection.add_custom_parameter(
			model_id=model_id,
			parameter_name='ShockSign',
			val_min=0.0,
			val_max=1.0,
			default=0.0
			)

		self._api_connection.add_custom_parameter(
			model_id=model_id,
			parameter_name='Shock',
			val_min=0.0,
			val_max=1.0,
			default=0.0
			)
		self._api_connection.add_custom_parameter(
			model_id=model_id,
			parameter_name='PosessedLook',
			val_min=0.0,
			val_max=1.0,
			default=1.0
			)
		sleep(3)


	def set_model_parameters(self, model_id, parameters:dict):
		if not model_id in self._models:
			raise ModelNotLoadedException

		self._api_connection.set_model_parameters(
			model_id=model_id,
			parameters=parameters
		)


	def set_actions(self, actions:list or tuple):
		self._actions={}
		self._processed_actions=[]
		
		af=Animation_Seq()
		for action in actions:
			af.add_action(action)

		self._actions = af.sequence

		m=0
		print('---')
		for action in self._actions:
			for prop in self._actions[action]:
				if len(self._actions[action][prop])>m:
					m=len(self._actions[action][prop])



		for index in range(1, m+1):
			ac=[]
			for action in self._actions:
				for prop in self._actions[action]:
					if len(self._actions[action][prop])>=index:
						if action=='speak':
							d={"action_name": action,"value":self._actions[action][prop][index-1]/100, 'prop': prop}

						elif action=='angry_sign':
							d={"action_name": action,"value":self._actions[action][prop][index-1]/100, 'prop': prop}

						elif action=='possessed_look':
							d={"action_name": action,"value":self._actions[action][prop][index-1]/100, 'prop': prop}

						elif action=='shock_sign':
							d={"action_name": action,"value":self._actions[action][prop][index-1]/100, 'prop': prop}

						elif action=='shock':
							d={"action_name": action,"value":self._actions[action][prop][index-1]/100, 'prop': prop}

						elif action=='blink':
							d={"action_name": action,"value":self._actions[action][prop][index-1]/100, 'prop': prop}

						elif action=='wink_left_eye' or action=='wink_right_eye' or action=='wink_left_eye_tilt' or action=='wink_right_eye_tilt':
							d={"action_name": action,"value":self._actions[action][prop][index-1]/100, 'prop': prop}

						elif action=='tilt_head_left' or action=='tilt_head_right':
							d={"action_name": action,"value":self._actions[action][prop][index-1]/100, 'prop': prop}

						else:
							d={"action_name": action,"value":self._actions[action][prop][index-1], 'prop': prop}

						ac.append(d)

			self._processed_actions.append(ac)
			
		for action in self._actions:
			print(action, self._actions[action])
			
		pprint(self._processed_actions)


	def play_actions(self, model_id):
		for actions_frame in self._processed_actions:
			parameters={}
			for action in actions_frame:
				parameters[action['prop']]=action['value']
			
			print(parameters)
			self.set_model_parameters(
				model_id=model_id,
				parameters=parameters)


