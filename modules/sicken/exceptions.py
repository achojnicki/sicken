#Main Sicken Exception
class SickenException(Exception):
	pass

#Sicken VTube plugin exceptions
class SickenVTubeException(SickenException):
	pass

class ModelException(SickenVTubeException):
	pass

class APIConnectionException(SickenVTubeException):
	pass

class RequestIdDoNotMatch(APIConnectionException):
	pass

class ModelNotLoadedException(ModelException):
	pass

#Sicken DB exceptions:
class SickenDBException(SickenException):
	pass

class ChatNotFoundException(SickenDBException):
	pass