import glob
import json
import re
import os
import os.path

from . import errors

class Server(object):
	"""
	A Minecraft server instance
	"""

	PROPERTIES_REGEX      = re.compile(r'^([a-zA-Z0-9\-]+)=([^#]+)( *#.*)?$')
	PROPERTIES_BOOL_REGEX = re.compile(r'^(true|false)$', re.IGNORECASE)
	PROPERTIES_INT_REGEX  = re.compile(r'^([0-9]+)$')
	SETTINGS_FILE         = 'mymcadmin.settings'

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

		if not self._jar and 'jar' in self.settings:
			self._jar = self.settings['jar']

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
					props = props_file.readlines()
			except FileNotFoundError:
				raise errors.ServerError(
					'Server properties file could not be found. ' +
					'Try starting the server first to generate one.'
				)

			self._properties = {}
			for line in props:
				match = Server.PROPERTIES_REGEX.match(line.strip())
				if not match:
					continue

				name, value, _ = match.groups()
				self._properties[name] = Server._convert_property_value(value)

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
		"""
		List all available servers
		"""

		path = config.instance_path

		# TODO(durandj): we could do some better checks
		return [
			os.path.join(path, f) for f in os.listdir(path)
			if os.path.isdir(os.path.join(path, f))
		]

	@classmethod
	def _convert_property_value(cls, value):
		"""
		Convert a value from the properties value to its correct type. IE
		integers are converted to ints, true/false to boolean, etc.
		"""

		if value == '':
			return None
		elif cls.PROPERTIES_BOOL_REGEX.match(value):
			return value.lower() == 'true'
		elif cls.PROPERTIES_INT_REGEX.match(value):
			return int(value)
		else:
			return value

