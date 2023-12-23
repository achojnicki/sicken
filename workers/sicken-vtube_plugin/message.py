from json import dumps

class Message:
	def __init__(
		self,
		message_type:str,
		request_id:int,
		data:dict,
		api_name:str="VTubeStudioPublicAPI",
		api_version:str="1.0",
		):
		
		self._api_name=api_name,
		self._api_version=api_version,
		self._message_type=message_type,
		self._request_id=request_id,
		self._data=data

	def _build_message(self):
		return {
		"apiName": self._api_name,
		"apiVersion": self._api_version,
		"requestID": self._request_id,
		"messageType": self._message_type,
		"data": self._data
		}

	def __str__(self):
		return dumps(self._build_message())