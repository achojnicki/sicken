from html import escape

import wx
import wx.html2
import wx.stc

class Chat_Page(wx.Panel):
    def __init__(self, root, parent, frame):
        self._root=root
        self._frame=frame
        wx.Panel.__init__(self, parent)

        self._chat_uuid=None
        self._user_uuid=None

        self.chat_template=open("views/chat.view",'r').read()
        self.sizer=wx.BoxSizer(wx.VERTICAL)        

        self.html=wx.html2.WebView.New(self)
        self.html.SetPage(self.chat_template,"")
        self.html.EnableContextMenu(False)
        self.html.EnableAccessToDevTools(False)

        self.textctrl=wx.TextCtrl(self,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.TE_PROCESS_ENTER
            )

        self.sizer.Add(self.html, 1, wx.EXPAND)
        self.sizer.Add(self.textctrl, 0, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.SetBackgroundColour((32,34,39))
    
        self.textctrl.Bind(wx.EVT_TEXT_ENTER, self.enter_event)
        
        self.Show(True)

    def parse_command(self, cmd):
        cmd=cmd.replace('/','')

        cmd=cmd.split(' ')
        command=cmd[0]
        del cmd[0]
        args=cmd

        return [command, args]


    def enter_event(self, event):
        msg=self.textctrl.GetValue()
        if msg!='':
            self.textctrl.SetValue("")
            self.add_user_message(msg)

            if msg[0]!='/':
                self._root._events.event(
                        event_name="message_entered",
                        event_data={
                            "chat_uuid": self._root._chat_uuid,
                            "message_author": "adrianchojnicki",
                            "message_source": "sicken-gui",
                            "message": msg 
                            }
                        )
            else:
                cmd, args=self.parse_command(msg)
                self._root._events.event(
                        event_name="command_entered",
                        event_data={
                            "chat_uuid": self._root._chat_uuid,
                            "message_author": "adrianchojnicki",
                            "message_source": "sicken-gui",
                            "cmd": cmd,
                            "args": args
                          }
                        )
            
    def add_user_message(self, message):
        message=message.replace('\\',"&#92;")
        message=escape(message)
        self.html.RunScript('add_user_message("{0}");'.format(message))

    def add_sickens_message(self, message, esc=True):
        message=message.replace('\r','')
        message=message.replace('\t','')
        
        if esc:
            message=escape(message)
        message=message.replace('\n','<br>')
        message=message.replace('\\',"&#92;")

        s='add_sickens_message("{0}");'.format(message)
        #print(s)
        wx.CallAfter(self.html.RunScript, s)

    def add_system_message(self, message, esc=True):
        message=message.replace('\r','')
        message=message.replace('\t','')
        
        if esc:
            message=escape(message)
            message=message.replace('\\',"&#92;")

        message=message.replace('\n','<br>')

        s='add_system_message("{0}");'.format(message)
        print(s)
        wx.CallAfter(self.html.RunScript, s)




