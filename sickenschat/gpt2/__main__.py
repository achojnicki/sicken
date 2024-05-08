#!/usr/bin/env python3
from sicken.gpt2 import Sicken
from gui import GUI
from adislog import adislog

import wx

class Main:
    def __init__(self):
        self.log=adislog(
            backends=['terminal_table'],
            debug=True,
            replace_except_hook=False,
            )

        self.app = wx.App(False)
        self.sicken=Sicken(self)
        self.gui=GUI(self)
        self.frame = self.gui

    def start(self):
        self.app.MainLoop()


if __name__=="__main__":
    app=Main()
    app.start()

