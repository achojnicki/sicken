from .system import System
from .inspect import Inspect
from .parent import Parent
from .traceback import Traceback

class Probes(System, Inspect, Parent, Traceback):
	def __init__(self, parent):
		self._parent=parent


