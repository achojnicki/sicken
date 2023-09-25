import wx
import wx.html2
import wx.stc
import Constants

class GUI(wx.Frame):
    def __init__(self, root):
        wx.Frame.__init__(self, None, title="Sicken's Chat", size=(800,600))

        self.root=root
        self.log=root.log
        self.chat_template=open(Constants.GUI.chat_template_t5_path,'r').read()

        self.sizer=wx.BoxSizer(wx.VERTICAL)

        self.model_choice=wx.Choice(self,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            choices=self.root.sicken.get_t5_models_list(),
            style=0
            )

        self.tokenizer_choice=wx.Choice(self,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            choices=self.root.sicken.get_t5_tokenizers_list(),
            style=0
            )
        

        self.html= wx.html2.WebView.New(self)
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
        self.sizer_choices=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_choices.Add(self.model_choice)
        self.sizer_choices.Add(self.tokenizer_choice)
        self.sizer.Add(self.sizer_choices, 0, wx.ALIGN_RIGHT)
        self.sizer.Add(self.textctrl, 0, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.SetBackgroundColour((32,34,39))
    
        self.textctrl.Bind(wx.EVT_TEXT_ENTER, self.enter_event)
        self.model_choice.Bind(wx.EVT_CHOICE, self.on_model_choice)
        self.tokenizer_choice.Bind(wx.EVT_CHOICE, self.on_tokenizer_choice)

        
        self.Show(True)

    def get_selected_model(self):
        return self.model_choice.GetStringSelection()
    
    def get_selected_tokenizer(self):
        return self.tokenizer_choice.GetStringSelection()

    def on_model_choice(self, event):
        self.log.info('Changing model...')
        self.root.sicken.set_model()
        self.log.success('Model changed to {model}'.format(model=self.get_selected_model()))
    
    def on_tokenizer_choice(self, event):
        self.log.info('Changing tokenizer...')
        self.root.sicken.set_tokenizer()
        self.log.success('Tokenizer changed to {tokenizer}'.format(tokenizer=self.get_selected_tokenizer()))


    def enter_event(self, event):
        msg=self.textctrl.GetValue()
        if msg!='':
            self.textctrl.SetValue("")
            self.add_adrians_message(msg)
            answers=self.root.sicken.get_answer(msg)
            for a in answers:
                self.log.success(a)
                self.add_sickens_message(a.replace('\n',"<br>").replace('"',"&quot;"))

    def add_adrians_message(self, message):
        self.html.RunScript('add_adrians_message("{0}");'.format(message))

    def add_sickens_message(self, message):
        self.html.RunScript('add_sickens_message("{0}");'.format(message))



