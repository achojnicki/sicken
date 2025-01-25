class Parent:
	@property        
	def parent(self):
		if hasattr(self._parent._parent, 'log_handle') and hasattr(self._parent._parent, 'project_name'):
			return self._parent._parent.log_handle.log_data
		return {}

	@property
	def project_name(self):
		if hasattr(self._parent._parent, 'project_name'):
			return self._parent._parent.project_name
		return "Unknown"
