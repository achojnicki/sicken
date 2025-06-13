from sicken.DB import DB


import wx
import wx.grid

class Detailed_Window(wx.Frame):
	def __init__(self, root, parent):
		self._root=root
		self._parent=parent

		self._classification_group=""
		self._classification_name=""
		self._classification_definition=""
		self._memory_value=""
		self._sickens_comment=""

		wx.Frame.__init__(self, self._parent, title="Details", size=(800,500), style=wx.DEFAULT_FRAME_STYLE)


		self._textctrl=wx.TextCtrl(self, wx.ID_ANY, size = wx.DefaultSize,
                         style = wx.TE_MULTILINE | wx.TE_READONLY)

		self._tree=wx.TreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
		self._tree_root=self._tree.AddRoot('Memory')
		self._classification_group_item=self._tree.AppendItem(self._tree_root, 'Clasification Group')
		self._classification_name_item=self._tree.AppendItem(self._tree_root, 'Classification Name')
		self._classification_definition_item=self._tree.AppendItem(self._tree_root, 'Classification Definition')
		self._memory_value_item=self._tree.AppendItem(self._tree_root, 'Memory Value')
		self._sickens_comment_item=self._tree.AppendItem(self._tree_root, 'Sicken\'s Comment')
		self._tree.Expand(self._tree_root)


		self._sizer=wx.BoxSizer(wx.HORIZONTAL)

		self._sizer.Add(self._tree, 3, wx.EXPAND)
		self._sizer.Add(self._textctrl, 8, wx.EXPAND)

		self.SetSizer(self._sizer)

		self.Bind(wx.EVT_CLOSE, self._on_close)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_select, self._tree) 
		self.SetMinSize((800,500))

	def _on_close(self, event=None):
		self.Hide()

	def _on_select(self, evt):
		if self._tree.GetSelection() == self._classification_group_item:
			self._textctrl.SetValue(self._classification_group)
		elif self._tree.GetSelection() == self._classification_name_item:
			self._textctrl.SetValue(self._classification_name)
		elif self._tree.GetSelection() == self._classification_definition_item:
			self._textctrl.SetValue(self._classification_definition)
		elif self._tree.GetSelection() == self._memory_value_item:
			self._textctrl.SetValue(self._memory_value)
		elif self._tree.GetSelection() == self._sickens_comment_item:
			self._textctrl.SetValue(self._sickens_comment)
		else:
			self._textctrl.SetValue("")

	def _set_data(self, classification_group, classification_name, classification_definition, memory_value, sickens_comment):
		self._classification_group=classification_group
		self._classification_name=classification_name
		self._classification_definition=classification_definition
		self._memory_value=memory_value
		self._sickens_comment=sickens_comment

		self._tree.SelectItem(self._tree_root)

class Memories_Page(wx.Panel):
	def __init__(self, root, parent, frame):
		self._root=root
		self._frame=frame

		self._db=self._root._db

		self._profiles={}
		self._profiles_indexes=[]

		self._memories={}
		self._memories_indexes=[]

		wx.Panel.__init__(self, parent)


		self._detailed_window=Detailed_Window(
			root=self._root,
			parent=self
			)

		self._profiles_list=wx.ListCtrl(self, id=wx.ID_ANY, style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
		self._profiles_list.InsertColumn(0, "User", width=200)

		self._memories_list=wx.ListCtrl(self, id=wx.ID_ANY, style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
		self._memories_list.InsertColumn(0, "Classification Group", width=200)
		self._memories_list.InsertColumn(1, "Classification", width=200)
		self._memories_list.InsertColumn(2, "Memory Value", width=500)
		self._memories_list.InsertColumn(3, "Sicken\'s Comment", width=500)
		




		self._left_sizer=wx.BoxSizer(wx.VERTICAL)
		self._left_sizer.Add(self._profiles_list, 1, wx.EXPAND)

		self._right_sizer=wx.BoxSizer(wx.VERTICAL)
		self._right_sizer.Add(self._memories_list, 8, wx.EXPAND)

		self._container_sizer=wx.BoxSizer(wx.HORIZONTAL)
		self._container_sizer.Add(self._left_sizer,2, wx.EXPAND)
		self._container_sizer.Add(self._right_sizer, 8, wx.EXPAND)

		self._main_sizer=wx.BoxSizer(wx.VERTICAL)
		self._main_sizer.Add(self._container_sizer, 2, wx.EXPAND)


		self.SetSizer(self._main_sizer)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_user_select, self._profiles_list)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_user_deselect, self._profiles_list)
		self.Bind(wx.EVT_LIST_COL_CLICK, self._on_sort, self._profiles_list)
		self.Bind(wx.EVT_LIST_COL_CLICK, self._on_sort, self._memories_list)
		#self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self._veto_event, self._profiles_list)
		#self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self._veto_event, self._memories_list)


		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_doubleclick, self._memories_list) 

		self._do_propagate_profiles()

	def _on_doubleclick(self, event):
		classification_group=self._db.get_classification_group_by_classification_group_uuid(
				classification_group_uuid=self._memories[self._memories_indexes[self._memories_list.GetFocusedItem()]]['classification_group_uuid'])

		classification_definition=self._db.get_classification_definition_by_classification_uuid(
				classification_uuid=self._memories[self._memories_indexes[self._memories_list.GetFocusedItem()]]['classification_uuid'])
		


		self._detailed_window._set_data(
			classification_group=classification_group['classification_group_name'],
			classification_name=classification_definition['classification_name'],
			classification_definition=classification_definition['classification_description'],
			memory_value=self._memories[self._memories_indexes[self._memories_list.GetFocusedItem()]]['memory_value'],
			sickens_comment=self._memories[self._memories_indexes[self._memories_list.GetFocusedItem()]]['sickens_comment'],
			)

		self._detailed_window.Show()

	def _veto_event(self, event):
		event.Veto()

	def _on_sort(self, event):
		self.Layout()
		self.Update()


	def _do_propagate_profiles(self, event=None):
		self._profiles=self._db.get_all_profiles()
		self._profiles_indexes=list(self._profiles.keys())
		
		self._profiles_list.DeleteAllItems()
		
		print(self._profiles)
		for profile in self._profiles:
			self._profiles_list.InsertItem(
				self._profiles_indexes.index(profile),
				self._profiles[profile]['profile_user_name']
			)
		self.Layout()
		self.Update()

	def _do_propagate_memories(self):
		self._memories=self._db.get_all_memories_with_user_by_profile_uuid(
			profile_uuid=self._profiles[self._profiles_indexes[self._profiles_list.GetFocusedItem()]]['profile_uuid']
			)
		self._memories_indexes=list(self._memories.keys())

		self._memories_list.DeleteAllItems()


		for memory_uuid in self._memories:
			classification_group=self._db.get_classification_group_by_classification_group_uuid(
				classification_group_uuid=self._memories[memory_uuid]['classification_group_uuid'])

			classification=self._db.get_classification_definition_by_classification_uuid(
				classification_uuid=self._memories[memory_uuid]['classification_uuid'])

			self._memories_list.InsertItem(
				self._memories_indexes.index(memory_uuid),
				classification_group['classification_group_name']
			)
			
			self._memories_list.SetItem(
				self._memories_indexes.index(memory_uuid),
				1,
				classification['classification_name']
			)

			self._memories_list.SetItem(
				self._memories_indexes.index(memory_uuid),
				2,
				str(self._memories[memory_uuid]['memory_value'])
			)

			self._memories_list.SetItem(
				self._memories_indexes.index(memory_uuid),
				3,
				str(self._memories[memory_uuid]['sickens_comment'])
			)



	def _on_user_select(self, event):
		self._do_propagate_memories()

	def _on_user_deselect(self,event):
		self._memories_list.DeleteAllItems()
	