from html import escape
from sys import exit
from os import getppid, kill

import wx
import wx.html2
import wx.stc


class Chat_Viewer_GUI(wx.Frame):
	def __init__(self, root):
		self._root=root

		self._config=root._config
		wx.Frame.__init__(self, None, title="sicken-chat_viewer", size=(self._config.window.width,self._config.window.height), style=wx.DEFAULT_FRAME_STYLE)

		self.chat_template=open("/opt/sicken/files/sicken/views/twitch_chat.html",'r').read()
		self.sizer=wx.BoxSizer(wx.VERTICAL)        

		self.html=wx.html2.WebView.New(self)
		self.html.SetPage(self.chat_template,"")
		self.html.EnableContextMenu(True)
		self.html.EnableAccessToDevTools(True)

		self.sizer.Add(self.html, 1, wx.EXPAND)
		self.SetSizer(self.sizer)

		self.SetBackgroundColour((32,34,39))
	
		self.SetMinSize((self._config.window.width,self._config.window.height))
		self.SetMaxSize((self._config.window.width,self._config.window.height))
		self.Show(True)
	

	def add_message_user(self, message):
		message['message']=message['message'].replace('\r','')
		message['message']=message['message'].replace('\t','')
		message['message']=escape(message['message'])
		message['message']=message['message'].replace('\n','<br>')

		s=f'add_message("{message["message_author"]}", "{message["message"]}","{message["message_source"]}");'
		wx.CallAfter(self.html.RunScript, s)

	def add_message_sicken(self, message):
		if message['speech']:
			message['speech']=message['speech'].replace('\r','')
			message['speech']=message['speech'].replace('\t','')
			message['speech']=escape(message['speech'])
			message['speech']=message['speech'].replace('\n','<br>')

			s=f'add_message("Sicken.AI", "{message["speech"]}");'
			wx.CallAfter(self.html.RunScript, s)


	def _on_close(self, event):
		self._root._active=False
		
		kill(getppid(), 15)
		exit(0)
		
