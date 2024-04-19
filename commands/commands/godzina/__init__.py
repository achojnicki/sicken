from time import strftime

class godzina:
	def __init__(self, root):
		self._root=root
		self._log=root._log

	def command(self):
		return strftime("%H:%M")