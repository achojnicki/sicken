from sicken.DB import DB


import wx
import wx.grid


class Memories_Page(wx.Panel):
	def __init__(self, root, parent, frame):
		self._root=root
		self._frame=frame

		self._db=self._root._db

		self._profiles={}
		self._profiles_indexes=[]

		wx.Panel.__init__(self, parent)

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

		self._do_propagate_profiles()
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
		memories=self._db.get_all_memories_with_user_by_profile_uuid(
			profile_uuid=self._profiles[self._profiles_indexes[self._profiles_list.GetFocusedItem()]]['profile_uuid']
			)
		indexes=list(memories.keys())

		self._memories_list.DeleteAllItems()

		print('111')
		print(memories)

		for memory_uuid in memories:
			classification_group=self._db.get_classification_group_by_classification_group_uuid(
				classification_group_uuid=memories[memory_uuid]['classification_group_uuid'])

			classification=self._db.get_classification_definition_by_classification_uuid(
				classification_uuid=memories[memory_uuid]['classification_uuid'])

			self._memories_list.InsertItem(
				indexes.index(memory_uuid),
				classification_group['classification_group_name']
			)
			
			self._memories_list.SetItem(
				indexes.index(memory_uuid),
				1,
				classification['classification_name']
			)

			self._memories_list.SetItem(
				indexes.index(memory_uuid),
				2,
				memories[memory_uuid]['memory_value']
			)

			self._memories_list.SetItem(
				indexes.index(memory_uuid),
				3,
				memories[memory_uuid]['sickens_comment']
			)



	def _on_user_select(self, event):
		self._do_propagate_memories()

	def _on_user_deselect(self,event):
		self._memories_list.DeleteAllItems()
	