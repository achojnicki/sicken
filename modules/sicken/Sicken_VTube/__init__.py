from sicken.exceptions import RequestIdDoNotMatch, ModelNotLoadedException, AuthFailedException

from websockets.sync.client import connect
from random import randint
from json import dumps, loads
from pprint import pprint
from base64 import b64encode
from time import time, sleep
from math import ceil
from pprint import pprint
from random import randint
import importlib.util
from sys import modules, exit

SICKEN_IMAGE="Sicken.jpg"
PLUGIN_NAME="Sicken.ai"
PLUGIN_DEVELOPER="adrianchojnicki.me"


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


class _API_Connectyion_Auth:
	@property
	def authenticated(self):
		return True if self._auth_token else False

	@property
	def auth_token(self):
		return self._auth_token

	def auth(self):
		try:
			request_id=self._generate_request_id()
			self._log.info('Staring authentication with VTube Studio...')
			self._log.info('Sending pre-auth message...')
			resp=self._request_response(
				request_data=self._message_builder.pre_auth_message(
					request_id=request_id
					)
				)

			if resp['requestID']!=request_id:
				raise RequestIdDoNotMatch

			if 'authenticationToken' in resp['data']:
				self._message_builder.auth_token=resp['data']['authenticationToken']
				self._auth_token=resp['data']['authenticationToken']
			else:
				raise AuthFailedException

			request_id=self._generate_request_id()

			self._log.info('Sending the authentication message')
			resp=self._request_response(
				request_data=self._message_builder.auth_message(
					request_id=request_id
					)
				)

			self._log.success('Authentication with VTube Studio succeeded.')
		
		except RequestIdDoNotMatch:
			self._log.error('Received a pre-auth message, but the RequestID do not match with the sent one.')
			exit(1)

		except AuthFailedException:
			self._log.error('Authentication with VTube Studio failed. You need to allow access for Sicken.AI')
			exit(1)


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
		self._log=root._log

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
		print(time()-t)
		#pprint(msg)
		#print('---')
		return msg

	def init_connection(self, host, port):
		self._connect(host=host, port=port)
		self.auth()

	def _connect(self, host, port):
		try:
			self._log.info(f"Connecting with VTube Studio at ws://{host}:{port}")
			self._connection=connect(f"ws://{host}:{port}")
			self._log.success("Connection with VTube Studio accomplished")
		except ConnectionRefusedError:
			self._log.error('Connection with VTube Studio failed. Is the studio running?')
			sleep(1)
			exit(1)

		except:
			self._log.exception('Exception occured during connecting')
			raise



class Animation_Seq:
	def __init__(self, root):
		self._root=root
		self._log=root._log

		self._frame=self._root._config.vtube.frame_duration
		self._live2d_model_manifest=self._root._live2d_model_manifest

		self._actions={}
		self._sequence={}
		self._words=[]
		self._duration=0.0

	def add_action(self, action):
		print(action)
		self._actions[action['action_name']]=action

	def _adaptive_smooth(self, int_list, alpha=0.4):
	    smoothed = [int_list[0]]  # keep first point

	    for i in range(1, len(int_list) - 1):
	        prev, curr, next_ = int_list[i - 1], int_list[i], int_list[i + 1]
	        neighbor_avg = (prev + next_) / 2
	        delta = neighbor_avg - curr
	        softened = round(curr + alpha * delta)
	        smoothed.append(softened)

	    smoothed.append(int_list[-1])  # keep last point
	    return smoothed
	
	def _causal_smooth(self, int_list, alpha=0.5):
	    smoothed = [int_list[0]]  # Start with the first value

	    for i in range(1, len(int_list)-1):
	        prev_smooth = smoothed[-1]
	        curr = int_list[i]
	        # Smooth only slightly toward previous smoothed value
	        new_val = round(prev_smooth + alpha * (curr - prev_smooth))
	        smoothed.append(new_val)

	    smoothed.append(int_list[-1])
	    return smoothed

	@property
	def sequence(self):
		if 'speak' in self._actions:
			self._duration=self._actions['speak']['duration']
			data={}

			for prop in self._live2d_model_manifest['actions']['speak']['parameters']:
				generator=getattr(self, self._live2d_model_manifest['actions']['speak']['parameters'][prop]['generator'])
				smoother=getattr(self, self._live2d_model_manifest['actions']['speak']['parameters'][prop]['smoother'])
				
				data[prop]=smoother(generator(
					self._actions['speak']['words'],
					self._live2d_model_manifest['actions']['speak']['parameters'][prop]['data']
				), alpha= self._live2d_model_manifest['actions']['speak']['parameters'][prop]['smoother_alpha'])

			self._sequence['speak']=data

		else:
			self._duration=1.0

		for action in self._actions:
			if not action in self._live2d_model_manifest['actions']:
				print('Action not defined in the manifest')

			if action in self._live2d_model_manifest['actions'] and action != 'speak':
				data={}
				for prop in self._live2d_model_manifest['actions'][action]['parameters']:
					generator=getattr(self, self._live2d_model_manifest['actions'][action]['parameters'][prop]['generator'])

					data[prop]=generator(
						start=self._live2d_model_manifest['actions'][action]['parameters'][prop]['start'],
						stop=self._live2d_model_manifest['actions'][action]['parameters'][prop]['stop'],
						step=self._live2d_model_manifest['actions'][action]['parameters'][prop]['step']
						)
				self._sequence[action]=data


		return self._sequence


class Model:
	def __init__(self, root):
		self._root=root
		self._log=root._log

		self._live2d_model_manifest=self._root._live2d_model_manifest
		self._generators_path=self._root._generators_path

		self._models=[]
		self._api_connection=self._root._api_connection

		self._actions={}
		self._processed_actions=[]

		try:
			self._log.info('Loading Model\'s generators')
			spec = importlib.util.spec_from_file_location("generators", self._generators_path)
			generators = importlib.util.module_from_spec(spec)
			modules["generators"] = generators
			spec.loader.exec_module(generators)
			self._generators=generators
			self._log.success('Generators loaded successfully.')
		except:
			self._log.exception('Exception occured during loading generators')
			raise

	def load_model(self, model_id):
		self._log.info(f'Loading model with model_id:{model_id}')
		model_id=self._api_connection.load_model(model_id)
		self._models.append(model_id)

		for custom_parameter in self._live2d_model_manifest['custom_parameters']:
			self._api_connection.add_custom_parameter(
				model_id=model_id,
				parameter_name=custom_parameter,
				val_min=self._live2d_model_manifest['custom_parameters'][custom_parameter]['min'],
				val_max=self._live2d_model_manifest['custom_parameters'][custom_parameter]['max'],
				default=self._live2d_model_manifest['custom_parameters'][custom_parameter]['default']
				)
		self._log.success('Model loaded successfully')

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
		
		af=self._generators.generators(self._root)

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
						if self._live2d_model_manifest['actions'][action]['parameters'][prop]['mode']=='divine':
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
			
			self.set_model_parameters(
				model_id=model_id,
				parameters=parameters)

