import wx
import wx.grid

colors={
	"DEBUG": wx.Colour(169,169,169),
	"ERROR": wx.Colour(139, 0, 0),
	"FATAL": wx.Colour(240, 0, 0),
	"WARNING": wx.Colour(180, 180,0),
	"SUCCESS":wx.Colour(1, 150, 32),

}

class Logs_Page(wx.Panel):
	def __init__(self, root, parent, frame):
		self._root=root
		self._frame=frame
		self._page=1

		wx.Panel.__init__(self, parent)

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


	def _add_item(self, message):
		self._grid.AppendRows(1)
		self._grid.SetCellValue(self._grid.NumberRows-1,0,message['strtime'])
		self._grid.SetCellValue(self._grid.NumberRows-1,1,message['project_name'])
		self._grid.SetCellValue(self._grid.NumberRows-1,2,message['log_level'])
		self._grid.SetCellValue(self._grid.NumberRows-1,3,message['message'])
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



		
	