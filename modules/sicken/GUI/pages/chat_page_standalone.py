from sicken.Live2D_Animations import Animation_Model

from html import escape
from OpenGL.GL import *
from OpenGL.GLUT import *
from yaml import safe_load
from pathlib import Path
from platform import system
from threading import Thread
from playsound import playsound
from time import sleep


import wx
import wx.html2
import wx.stc
import wx.glcanvas as glcanvas
import live2d.v3 as live2d
import IPython


class MyCanvasBase(glcanvas.GLCanvas):
    def __init__(self, parent, *args, **kwargs):
        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.init = False
        self.context = glcanvas.GLContext(self)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)


    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

class SickenCanvas(MyCanvasBase):
    def __init__(self, parent, root):
        MyCanvasBase.__init__(self, parent)

        self._root=root
        self._live2d_model=None


        self.refresh_timer=wx.Timer(self)
        self.animation_timer=wx.Timer(self)


        self.Bind(wx.EVT_TIMER, self.on_refresh, self.refresh_timer)
        
        self.refresh_timer.Start(int(self._root._config.live2d.refresh_delay*1000))

    def OnMouseMotion(self, evt):
        x, y = evt.GetPosition()
        if self._live2d_model:
            self._live2d_model.Drag(x,y)

    def on_refresh(self, event):
        self.Refresh()


    def OnSize(self, event):
        wx.CallAfter(self.DoSetViewport)
        if self._live2d_model:
            pass
            #self._live2d_model.SetOffset(0,0)
            self._live2d_model.Resize(*self.GetSize())
        #event.Skip()


    def DoSetViewport(self):
        size = self.size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)


    def InitGL(self):
        live2d.glInit()

    def OnDraw(self):
        live2d.clearBuffer()

        if self._live2d_model:
            self._live2d_model.Update()
            self._live2d_model.Draw()

        self.SwapBuffers()


class Chat_Page_Standalone(wx.Panel):
    def __init__(self, root, parent, frame):
        self._root=root
        self._frame=frame
        wx.Panel.__init__(self, parent)

        self._active=True

        self._speeches={}
        self._is_speaking=False
        self._awaiting=[]

        self.awaiting_thread()

        self._chat_uuid=None
        self._user_uuid=None

        self.chat_template=open("views/chat.view",'r').read()

        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.inner_sizer=wx.BoxSizer(wx.HORIZONTAL)

        self.canvas=SickenCanvas(self, self._root)

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


        self.inner_sizer.Add(self.canvas, 7, wx.EXPAND)
        self.inner_sizer.Add(self.html, 5, wx.EXPAND)
        self.sizer.Add(self.inner_sizer, 9, wx.EXPAND)
        self.sizer.Add(self.textctrl, 0, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.SetBackgroundColour((32,34,39))
    
        self._speech_dir=Path(self._root._config.directories_posix.speech if system()=='Linux' or system()=='Darwin' else self._root._config.directories_nt.speech)
        self._model_path=Path(self._root._config.directories_posix.live2d_models if system()=='Linux' or system()=='Darwin' else self._root._config.directories_nt.live2d_models).joinpath(self._root._config.live2d.model).joinpath('model.yaml')
        self._generators_path=Path(self._root._config.directories_posix.live2d_models if system()=='Linux' or system()=='Darwin' else self._root._config.directories_nt.live2d_models).joinpath(self._root._config.live2d.model).joinpath('generators.py')
        self._live2d_model_path=Path(self._root._config.directories_posix.live2d_models if system()=='Linux' or system()=='Darwin' else self._root._config.directories_nt.live2d_models).joinpath(self._root._config.live2d.model).joinpath('model')

        with open(self._model_path, 'r') as file:
            self._live2d_model_manifest=safe_load(file.read())

        self._model3_path=Path(self._live2d_model_path).joinpath(self._live2d_model_manifest['model']['model3_file'])

        self._animation_model=Animation_Model(self, self._root)

        self.textctrl.Bind(wx.EVT_TEXT_ENTER, self.enter_event)

        self.Show(True)
    
    def _awaiting_thread(self):
        while self._active:
            if not self._is_speaking:
                for item in list(self._awaiting):
                    actions=self._speeches[item]['actions']

                    if not self._is_speaking:
                        self._model.set_actions(actions=actions)
                        self.play_sound(self._speech_dir.joinpath(f"{item}.mp3"))
                        self._model.play_actions(self._live2d_model_manifest['model']['model_id'])

                        del self._speeches[item]
                        del self._awaiting[self._awaiting.index(item)]
                    break
            sleep(1)

    def awaiting_thread(self):
        t=Thread(target=self._awaiting_thread, args=[])
        t.daemon=True
        t.start()

    def _play_sound(self, file):
        playsound(str(file))

    def play_sound(self, file):
        t=Thread(target=self._play_sound, args=[file])
        t.daemon=True
        t.start()

    def update_parameters(self, param_id, value):
        if self._live2d_model:
            print(param_id, value)
            self._live2d_model.SetParameterValue(param_id, value)


    def update_model(self):
        if self._live2d_model:
            self._live2d_model.Update()
            self.canvas.on_refresh(None)


    def init_canvas(self):
        self._live2d_model=live2d.LAppModel()
        self._live2d_model.LoadModelJson(str(self._model3_path))
        self._live2d_model.Resize(*self.canvas.GetSize())
        self._live2d_model.SetAutoBlinkEnable(False)
        self._live2d_model.SetAutoBreathEnable(False)
        self.canvas._live2d_model=self._live2d_model

    def enter_event(self, event):
        msg=self.textctrl.GetValue()
        if msg!='':
            self.textctrl.SetValue("")
            self.add_user_message(msg)

            self._root._events.event(
                    event_name="message_entered",
                    event_data={
                        "chat_uuid": self._root._chat_uuid,
                        "message_author": "Unknown",
                        "message_source": "sicken-gui",
                        "message": msg 
                        }
                    )
            
            
    def add_user_message(self, message):
        message=escape(message)
        self.html.RunScript('add_user_message("{0}");'.format(message))

    def add_sickens_message(self, message):
        message=message.replace('\r','')
        message=message.replace('\t','')
        message=escape(message)
        message=message.replace('\n','<br>')

        s='add_sickens_message("{0}");'.format(message)
        print(s)
        wx.CallAfter(self.html.RunScript, s)




