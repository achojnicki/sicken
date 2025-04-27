from platform import node
from os import getpid, getppid, getcwd


class System:
    @property
    def node(self):
        return node()

    @property
    def pid(self):
        return getpid()

    @property
    def ppid(self):
        return getppid()

    @property
    def cwd(self):
        return getcwd()

