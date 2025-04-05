from platform import node
from os import getpid, getppid, getcwd, getlogin, getuid, getgid


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

    @property
    def uid(self):
        return getuid()

    @property
    def gid(self):
        return getgid()

