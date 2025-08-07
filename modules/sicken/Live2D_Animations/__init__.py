from random import randint
from json import dumps, loads
from pprint import pprint
from time import time
from math import ceil
from pprint import pprint
from random import randint
from sys import modules, exit
from IPython import embed
from wx import CallAfter, CallLater
from time import sleep

import importlib.util

class Animation_Seq:
	def __init__(self, parent, root):
		self._root=root
		self._parent=parent
		self._log=root._log

		self._frame=self._parent._config.live2d.frame_duration
		self._live2d_model_manifest=self._parent._live2d_model_manifest

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
				if self._live2d_model_manifest['actions']['speak']['parameters'][prop]['smoother']:
					smoother=getattr(self, self._live2d_model_manifest['actions']['speak']['parameters'][prop]['smoother'])
				
				d=generator(
					self._actions['speak']['words'],
					self._live2d_model_manifest['actions']['speak']['parameters'][prop]['data']
				)
				
				if self._live2d_model_manifest['actions']['speak']['parameters'][prop]['smoother']:
					data[prop]=smoother(d,alpha= self._live2d_model_manifest['actions']['speak']['parameters'][prop]['smoother_alpha'])
				else:
					data[prop]=d

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


class Animation_Model:
	def __init__(self, parent, root):
		self._root=root
		self._parent=parent
		self._log=root._log

		self._config=self._root._config

		self._live2d_model_manifest=self._parent._live2d_model_manifest
		self._generators_path=self._parent._generators_path

		self._models=[]

		self._actions={}
		self._processed_actions=[]
		self._animation_frame=0
		self._play_actions=False

		self._frame_duration=self._root._config.live2d.frame_duration

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



	def set_actions(self, actions:list or tuple):
		self._actions={}
		self._processed_actions=[]
		
		af=self._generators.generators(self, self._root)

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

	def clean_actions(self):
		self._actions={}
		self._processed_actions=[]
		self._play_actions=False
		self._animation_frame=0

	def play_actions(self):
		self._play_actions=True

	def play_action_frame(self,timestamp,):
		if self._processed_actions and self._play_actions:

			actions_frame=self._processed_actions[self._animation_frame]
			parameters={}
			for action in actions_frame:
				parameters[action['prop']]=action['value']
			

			for param in parameters:
				self._parent.update_parameters(
					param_id=self._live2d_model_manifest['parameters_mapping'][param],
					value=parameters[param])
			self._parent.update_model()


			if self._animation_frame+1==len(self._processed_actions):
				self.clean_actions()
			else:
				self._animation_frame+=1