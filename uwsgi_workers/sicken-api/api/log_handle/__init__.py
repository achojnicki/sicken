from flask import request
class Log_Handle:
	def __init__(self, root):
		self._root=root
		self._db=root.db

		self._request=None
		self._form=None

	@property
	def request(self):
		if not self._request:
			return None

		return self._request
	
	@request.setter
	def request(self, request):
		self._request=request
		self._form=request.form

	@property
	def form(self):
		if not self._request:
			return None
		return self._form

	@property
	def user_agent(self):
		if not self._request:
			return None

		return str(self._request.user_agent)
	
	@property
	def url(self):
		if not self._request:
			return None
		return self._request.url


	@property
	def remote_addr(self):
		if not self._request:
			return None

		if self._request.headers.getlist("X-Forwarded-For"):
			remote_addr=self._request.headers.getlist("X-Forwarded-For")[0]
		else:
			remote_addr=self._request.remote_addr
		return str(remote_addr)

	@property
	def session_uuid(self):
		if not self._request:
			return None
		
		if 'session_uuid' in self.form:
			return self._form['session_uuid']
		else:
			return None

	@property
	def logged_in(self):
		if not self._request:
			return None

		if not self.session_uuid:
			return False

		return self._db.session_exists(self.session_uuid)
	
	@property
	def user(self):
		if not self._request:
			return None
		
		if not self.logged_in:
			return None

		session=self._db.get_session_by_session_uuid(self.session_uuid)
		user=self._db.get_user_by_user_uuid(session['user_uuid'])

		del user['_id']
		del user['password_hash']
		return user

	@property
	def session(self):
		if not self._request:
			return None
		
		if not self.logged_in:
			return None

		session=self._db.get_session_by_session_uuid(self.session_uuid)
		
		del session['_id']
		return session

	@property
	def log_data(self):
		data={
			"user_agent": self.user_agent,
			"remote_addr": self.remote_addr,
			"url":self.url,

			"logged_in": self.logged_in,
			"session_uuid": self.session['session_uuid'] if self.logged_in else None,
			"user_uuid": self.user['user_uuid'] if self.logged_in else None,

		}
		return data