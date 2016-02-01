import glob
import json
import os
import os.path

from . import errors

class Server(object):
	"""
	A Minecraft server instance
	"""

	SETTINGS_FILE = 'mymcadmin.settings'

	def __init__(self, path):
		"""
		Create an instance of the Minecraft server at the given file path.
		This does not create a new Minecraft server, instead its used to model
		a server.
		"""

		self._path            = path
		self._jar             = None
		self._properties_file = os.path.join(path, 'server.properties')
		self._properties      = None
		self._settings_file   = os.path.join(path, Server.SETTINGS_FILE)
		self._settings        = None

	@property
	def path(self):
		"""
		Get the file path of the server
		"""

		return self._path

	@property
	def jar(self):
		"""
		Get the server Jar to run
		"""

		if not self._jar:
			# TODO(durandj): check the settings file
			pass

		if not self._jar:
			jars = glob.glob(os.path.join(self._path, '*.jar'))

			if len(jars) == 0:
				raise errors.ServerError('No server jar could be found')
			elif len(jars) == 1:
				raise errors.ServerError('Unable to determine server jar')

			self._jar = jars[0]

		return self._jar

	@property
	def properties(self):
		"""
		Get the Minecraft server properties defined in the server.properties
		file
		"""

		if not self._properties:
			try:
				with open(self._properties_file, 'r') as props_file:
					self._properties = props_file.read() # TODO(durandj): parse this
			except FileNotFoundError:
				raise errors.ServerError(
					'Server properties file could not be found. ' +
					'Try starting the server first to generate one.'
				)

		return self._properties

	@property
	def settings(self):
		"""
		Get the MyMCAdmin settings for this server that are defined in the
		mymcadmin.settings file
		"""

		if not self._settings:
			with open(self._settings_file, 'r') as settings_file:
				self._settings = json.load(settings_file)

		return self._settings

	def start(self):
		"""
		Start the Minecraft server
		"""

		raise NotImplementedError

	def stop(self):
		"""
		Stop the Minecraft server
		"""

		raise NotImplementedError

	def restart(self):
		"""
		Restart the Minecraft server. This is an alias of stop and start
		"""

		self.stop()
		self.start()

	@staticmethod
	def list_all(config):
		path = config.instance_path

		# TODO(durandj): we could do some better checks
		return [
			os.path.join(path, f) for f in os.listdir(path)
			if os.path.isdir(os.path.join(path, f))
		]

