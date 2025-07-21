from sicken.GUI.pages.chat_page import Chat_Page
from sicken.GUI.pages.logs_page import Logs_Page
from sicken.GUI.pages.memories_page import Memories_Page

from platform import system
from sys import exit
from os import getppid, kill
from signal import SIGTERM
import wx


class Sicken_GUI(wx.Frame):
	def __init__(self, root):
		self._root=root
		wx.Frame.__init__(self, None, title="Sicken.ai", size=(750,810), style=wx.DEFAULT_FRAME_STYLE)

		self._notebook=wx.Notebook(self)
		self._chat_page=Chat_Page(self._root, self._notebook, self)
		self._logs_page=Logs_Page(self._root, self._notebook, self)
		self._memories_page=Memories_Page(self._root, self._notebook, self)

		self._notebook.AddPage(self._chat_page, "Chat")
		self._notebook.AddPage(self._logs_page, "Logs")
		self._notebook.AddPage(self._memories_page, "Memories")

		self.Bind(wx.EVT_CLOSE, self._on_close)

	def _on_close(self, event):
		self._root._active=False
		
		kill(getppid(), SIGTERM if system()=="Linux" or system()=="Darwin" else 0)
		exit(0)
		
