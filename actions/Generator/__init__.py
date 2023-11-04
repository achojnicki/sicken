from Constants import Generator_Constants
from json import loads, dumps
from pprint import pprint

class Generator:
	def __init__(self, root):
		self.root=root
		self.msg=[]

	def append_message(self, role, content):
		self.msg.append(
			{
				"role": role,
				"content": str(content)
			}
		)
	
	def init(self):
		av_functions=dumps(self.root.actions.get_functions_of_all_actions_groups())

		self.append_message(
			role="system",
			content=Generator_Constants.system_message
		)
		
		self.append_message(
			role="user",
			content="Avaiable functions:  {functions}".format(functions=av_functions)
		)
		
		self.append_message(
			role="assistant",
			content="ACK"
		)
		
		self.append_message(
			role="user",
			content="Print test123 to terminal."
		)

		self.append_message(
			role="assistant",
			content=dumps(Generator_Constants.test_resp)
		)

		self.append_message(
			role='user',
			content="""pretty print on terminal: {"a":1,"b":[1,2,3,4,5,6,7,7,8,8,8,8,8,8,8,8,8,8,8,8],"c":3}""")

	def print_msg(self):
		pprint(self.msg)
