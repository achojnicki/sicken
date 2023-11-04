from Actions.Actions.Base import Base_Class

from pprint import pprint

class Terminal(Base_Class):
	def __init__(self):
		super().__init__()

	def print_to_terminal(self, data:str):
		print(data)

	def pprint_to_terminal(self, data:str):
		pprint(data)

	functions=[
		{
			"name": "print_to_terminal",
			"description" : "Print data to terminal.",
			"callback": print_to_terminal, 
			"args":[
				{"name":"data", "type":"str"},
				]
		},
		{
			"name": "pprint_to_terminal",
			"description" : "Pretty print data to terminal.",
			"callback": pprint_to_terminal, 
			"args":[
				{"name":"data", "type":"str"},
				]
		},
	]

