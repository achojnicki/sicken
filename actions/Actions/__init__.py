from Actions.Actions import Terminal

import copy


class ActionsError(Exception):
	pass

class ActionGroupClassNotFound(ActionsError):
	pass

class FunctionNotFound(ActionsError):
	pass


class Actions:
	def __init__(self, root):
		self.root=root

		for a in self.actions:
			a['instance']=a['class']()

	def _pop_callback(self, data):
		data=copy.deepcopy(data)
		for a in data:
			a.pop('callback')
		return data

	def get_actions_group(self, action_group):
		for a in self.actions:
			if a['name']==action_group:
				return a
		raise ActionGroupClassNotFound

	def get_actions_groups(self):
		"""Return list of all actions groups"""
		d=[]
		for a in self.actions:
			d.append(a['name'])
		return d

	def get_actions_group_class(self, c):
		for a in self.actions:
			if a['name']==c:
				return a['class']
		raise ActionGroupClassNotFound


	def get_functions_of_actions_group(self, action_group):
		for a in self.actions:
			if a['name']==action_group:
				return self._pop_callback(a['functions'])

		raise ActionGroupClassNotFound

	def get_functions_of_all_actions_groups(self):
		data={}
		act=self.get_actions_groups()
		for a in act:
			data[a]=self.get_functions_of_actions_group(a)
		return data

	def execute_from_actions_group(self, actions_group, function, data):
		action_group=self.get_actions_group(actions_group)
		for a in action_group['functions']:
			if a['name']==function:
				return a['callback'](action_group['instance'],**data)
		raise FunctionNotFound

	def execute(self, data):
		results=[]
		for action in data:
			results.append(self.execute_from_actions_group(
				actions_group=action['actions_group'],
				function=action['action'],
				data=action['data']
			))



	actions=[
		{
			"name"      : "Terminal",
		 	"class"     : Terminal.Terminal,
		 	"instance"  : None,
		 	"functions" : Terminal.Terminal.functions
		},
]

