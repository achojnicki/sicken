from inspect import stack, currentframe

class Inspect:
    @property
    def caller(self):
        i=stack()[3]
        resp={"filename":str(i.filename),
              "function": str(i.function),
              "line_number":str(i.lineno)}
        return resp