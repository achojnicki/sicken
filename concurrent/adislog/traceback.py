from sys import exc_info
from traceback import extract_tb



class traceback:
	def __init__(self):
		pass

	def get_exception(self):
		ex_type, ex_value, ex_traceback=exc_info()
		tb=extract_tb(ex_traceback)

		stack=[]
		for stack_item in tb:
			item={
				"file": stack_item[0],
				"line": stack_item[1],
				"function": stack_item[2],
				"code": stack_item[3]
			}
			stack.append(item)

		excpt={
			"exception_type": ex_type.__name__,
			"exception_message": ex_value,
			"exception_stack_trace": stack,
			}
		return excpt