from html import escape
from sys import exit
from os import getppid, kill

import wx
import wx.html2
import wx.stc


class Bottom_Bar_GUI(wx.Frame):
	def __init__(self, root):
		self._root=root

		self._config=root._config
		wx.Frame.__init__(self, None, title="sicken-bottom_bar", size=(self._config.window.width,self._config.window.height), style=wx.DEFAULT_FRAME_STYLE)

		self.chat_template=open("/opt/sicken/files/sicken/views/bottom_bar/bottom_bar.html",'r').read()
		self.sizer=wx.BoxSizer(wx.VERTICAL)        

		self.html=wx.html2.WebView.New(self)
		self.html.SetPage(self.chat_template,"file:///opt/sicken/files/sicken/views/bottom_bar/bottom_bar.html")
		self.html.EnableContextMenu(True)
		self.html.EnableAccessToDevTools(True)

		self.sizer.Add(self.html, 1, wx.EXPAND)
		self.SetSizer(self.sizer)

		self.SetBackgroundColour((32,34,39))
	
		
		self.Show(True)
		

	def add_subtitles(self, message):
		if message['speech']:
			message['speech']=message['speech'].replace('\r','')
			message['speech']=message['speech'].replace('\t','')
			message['speech']=escape(message['speech'])
			message['speech']=message['speech'].replace('\n','<br>')

			s=f'add_subtitles("{message["speech"]}");'
			wx.CallAfter(self.html.RunScript, s)


	def _on_close(self, event):
		self._root._active=False
		
		kill(getppid(), 15)
		exit(0)
		
