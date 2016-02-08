class MyMCAdminError(Exception):
	"""
	A general MyMCAdmin error
	"""

	def __init__(self, message, *args, **kwargs):
		self.message = message.format(*args, **kwargs)

		super(MyMCAdminError, self).__init__(self.message)

class ConfigurationError(Exception):
	"""
	An error in a configuration of MyMCAdmin
	"""

class ServerError(Exception):
	"""
	An error with the Minecraft server
	"""

class ServerCreationError(ServerError):
	"""
	An error with creating a new Minecraft server
	"""

class ServerSettingsError(ServerError):
	"""
	An error in the MyMCAdmin settings for the server
	"""

