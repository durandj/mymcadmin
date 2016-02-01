class MyMCAdminError(Exception):
	"""
	A general MyMCAdmin error
	"""

	def __init__(self, message, *args, **kwargs):
		super(MyMCAdmin, self).__init__(message.format(*args, **kwargs))

class ConfigurationError(Exception):
	"""
	An error in a configuration of MyMCAdmin
	"""

class ServerError(Exception):
	"""
	An error with the Minecraft server
	"""

