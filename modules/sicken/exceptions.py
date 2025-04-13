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

class AuthFailedException(APIConnectionException):
	pass

class ModelNotLoadedException(ModelException):
	pass

#Sicken DB exceptions:
class SickenDBException(SickenException):
	pass

class ChatNotFoundException(SickenDBException):
	pass

class ClassificationGroupNotFoundException(SickenDBException):
	pass

class UserProfileNotFoundException(SickenDBException):
	pass

class UserProfileAlreadyExistsException(SickenDBException):
	pass

class MemoryDoesntExistsException(SickenDBException):
	pass