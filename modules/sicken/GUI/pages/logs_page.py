import wx
import wx.grid
from pprint import pformat

colors={
	"DEBUG": wx.Colour(169,169,169),
	"ERROR": wx.Colour(139, 0, 0),
	"FATAL": wx.Colour(240, 0, 0),
	"WARNING": wx.Colour(180, 180,0),
	"SUCCESS":wx.Colour(1, 150, 32),

}


class Detailed_Window(wx.Frame):
	def __init__(self, root, parent):
		self._root=root
		self._parent=parent

		self._log_message=""
		self._stack_trace={}
		self._caller={}
		self._system={}

		wx.Frame.__init__(self, self._parent, title="Details", size=(800,500), style=wx.DEFAULT_FRAME_STYLE)


		self._textctrl=wx.TextCtrl(self, wx.ID_ANY, size = wx.DefaultSize,
                         style = wx.TE_MULTILINE | wx.TE_READONLY)

		self._tree=wx.TreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
		self._tree_root=self._tree.AddRoot('Message')
		self._log_message_item=self._tree.AppendItem(self._tree_root, 'Log Message')
		self._stack_trace_item=self._tree.AppendItem(self._tree_root, 'Stack Trace')
		self._system_item=self._tree.AppendItem(self._tree_root, 'System')
		self._caller_item=self._tree.AppendItem(self._tree_root, 'Caller')
		self._tree.Expand(self._tree_root)


		self._sizer=wx.BoxSizer(wx.HORIZONTAL)

		self._sizer.Add(self._tree, 2, wx.EXPAND)
		self._sizer.Add(self._textctrl, 8, wx.EXPAND)

		self.SetSizer(self._sizer)

		self.Bind(wx.EVT_CLOSE, self._on_close)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_select, self._tree) 
		self.SetMinSize((800,500))

	def _on_close(self, event=None):
		self.Hide()

	def _on_select(self, evt):
		if self._tree.GetSelection() == self._log_message_item:
			self._textctrl.SetValue(self._log_message)
		elif self._tree.GetSelection() == self._stack_trace_item:
			self._textctrl.SetValue(pformat(self._stack_trace) if self._stack_trace else "")
		elif self._tree.GetSelection() == self._caller_item:
			self._textctrl.SetValue(pformat(self._caller) if self._caller else "")
		elif self._tree.GetSelection() == self._system_item:
			self._textctrl.SetValue(pformat(self._system) if self._system else "")	
		else:
			self._textctrl.SetValue("")

	def _set_data(self, log_message, stack_trace, caller, system):
		self._log_message=log_message
		self._stack_trace=stack_trace
		self._caller=caller
		self._system=system

		self._tree.SelectItem(self._tree_root)
			


class Logs_Page(wx.Panel):
	def __init__(self, root, parent, frame):
		self._root=root
		self._frame=frame

		self._log_data=[]
		wx.Panel.__init__(self, parent)

		self._detailed_window=Detailed_Window(
			root=self._root,
			parent=self
			)


		self._grid=wx.grid.Grid(self)
		self._grid.CreateGrid(0,9)
		self._grid.EnableEditing(False)

		self._grid.SetColLabelValue(0, "Datetime")
		self._grid.SetColSize(0, 150)

		self._grid.SetColLabelValue(1, "Project Name")
		self._grid.SetColSize(1, 200)

		self._grid.SetColLabelValue(2, "Log Level")
		self._grid.SetColSize(2, 70)

		self._grid.SetColLabelValue(3, "Message")
		self._grid.SetColSize(3, 800)

		self._grid.SetColLabelValue(4, "PID")
		self._grid.SetColSize(4, 50)

		self._grid.SetColLabelValue(5, "PPID")
		self._grid.SetColSize(5, 50)

		self._grid.SetColLabelValue(6, "Line Number")
		self._grid.SetColSize(6, 80)

		self._grid.SetColLabelValue(7, "Function")
		self._grid.SetColSize(7, 200)

		self._grid.SetColLabelValue(8, "File")
		self._grid.SetColSize(8, 900)

		self._sizer=wx.BoxSizer(wx.VERTICAL)
		self._sizer.Add(self._grid, 1, wx.EXPAND)
		self._main_sizer=wx.BoxSizer(wx.HORIZONTAL)
		self._main_sizer.Add(self._sizer, 1, wx.EXPAND)
		self.SetSizer(self._main_sizer)

		self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._on_doubleclick, self._grid) 


	def _on_doubleclick(self, event):
		self._detailed_window._set_data(
			log_message=self._log_data[event.GetRow()]['message'],
			stack_trace=self._log_data[event.GetRow()]['exception_data'],
			caller=self._log_data[event.GetRow()]['caller'],
			system=self._log_data[event.GetRow()]['system'],
			)

		self._detailed_window.Show()
	def _add_item(self, message):
		self._log_data.append(message)
		self._grid.AppendRows(1)
		self._grid.SetCellValue(self._grid.NumberRows-1,0,message['strtime'])
		self._grid.SetCellValue(self._grid.NumberRows-1,1,message['project_name'])
		self._grid.SetCellValue(self._grid.NumberRows-1,2,message['log_level'])
		self._grid.SetCellValue(self._grid.NumberRows-1,3,message['message'][0:100])
		self._grid.SetCellValue(self._grid.NumberRows-1,4,str(message['system']['pid']))
		self._grid.SetCellValue(self._grid.NumberRows-1,5,str(message['system']['ppid']))
		self._grid.SetCellValue(self._grid.NumberRows-1,6,str(message['caller']['line_number']))
		self._grid.SetCellValue(self._grid.NumberRows-1,7,message['caller']['function'])
		self._grid.SetCellValue(self._grid.NumberRows-1,8,message['caller']['filename'])


		attr=wx.grid.GridCellAttr()
		font=wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
		attr.SetFont(font)
		self._grid.SetAttr(self._grid.NumberRows-1, 2, attr)
		self._grid.SetCellAlignment(self._grid.NumberRows-1, 2, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

		if message['log_level'] in colors:
			for x in range(9):
				self._grid.SetCellBackgroundColour(self._grid.NumberRows-1, x, colors[message['log_level']])



		
	