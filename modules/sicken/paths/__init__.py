try:
	from sicken.config import Config
except:
	from modules.sicken.config import Config
	
from platform import system


class PathStringNotFound(Exception):
	pass

class PathForOSNotDefined(Exception):
	pass

class Paths:
	project_name="sicken-paths"
	def __init__(self):
		self._config=Config(self)

	def __call__(self, pathstring):
		if not self._config.has_category(pathstring):
			raise PathStringNotFound

		try:
			if system() in ["Linux", "Darwin"]:
				return self._config[pathstring].posix
			else:
				return self._config[pathstring].nt
		except:
			raise PathForOSNotDefined
