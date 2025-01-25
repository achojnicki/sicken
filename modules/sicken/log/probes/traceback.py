from sys import exc_info
from traceback import extract_tb


class Traceback:
    @property
    def exception(self):
        ex_type, ex_value, ex_traceback=exc_info()
        tb=extract_tb(ex_traceback)

        stack=[]
        for stack_item in tb:
            item={
                "file": str(stack_item[0]),
                "line": str(stack_item[1]),
                "function": str(stack_item[2]),
                "code": str(stack_item[3])
            }
            stack.append(item)

        excpt={
            "exception_type": str(ex_type.__name__),
            "exception_message": str(ex_value),
            "exception_stack_trace": stack,
            }
        return excpt