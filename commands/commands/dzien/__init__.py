from time import strftime

class dzien:
	def __init__(self, root):
		self._root=root
		self._log=root._log

	def command(self):
		return strftime("%A %d/%m")