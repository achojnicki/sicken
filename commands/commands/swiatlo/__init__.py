from time import strftime

class swiatlo:
	def __init__(self, root):
		self._root=root
		self._log=root._log

	def command(self, lokalizacja=None, flat=None):
		return "Światło" if not lokalizacja else f"Śwatło.\nlokalizacja: {lokalizacja}\n flat: {flat}"