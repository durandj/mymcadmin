import asyncio
import glob
import json
import logging
import re
import os
import os.path

from . import client, errors

class Server(object):
	"""
	A Minecraft server instance
	"""

	LOG_FILE              = 'mymcadmin.log'
	PID_FILE              = 'server.pid'
	PROPERTIES_FILE       = 'server.properties'
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
		self._cache           = {}
		self._admin_log       = os.path.join(path, Server.LOG_FILE)
		self._pid_file        = os.path.join(path, Server.PID_FILE)
		self._properties_file = os.path.join(path, Server.PROPERTIES_FILE)
		self._properties      = None
		self._settings_file   = os.path.join(path, Server.SETTINGS_FILE)
		self._settings        = None

	@property
	def pid_file(self):
		"""
		Get the instance PID
		"""

		return self._pid_file

	@property
	def path(self):
		"""
		Get the file path of the server
		"""

		return self._path

	@property
	def name(self):
		"""
		Get the server name
		"""

		return os.path.basename(self._path)

	@property
	def java(self):
		"""
		Get the Java binary to use
		"""

		if 'java' not in self._cache:
			self._cache['java'] = self._settings.get('java', 'java')

		return self._cache['java']

	@property
	def jar(self):
		"""
		Get the server Jar to run
		"""

		if 'jar' not in self._cache and 'jar' in self.settings:
			self._cache['jar'] = self.settings['jar']

		if 'jar' not in self._cache:
			jars = glob.glob(os.path.join(self._path, '*.jar'))

			if len(jars) == 0:
				raise errors.ServerError('No server jar could be found')
			elif len(jars) > 1:
				raise errors.ServerError('Unable to determine server jar')

			self._cache['jar'] = jars[0]

		return self._cache['jar']

	@property
	def command_args(self):
		"""
		Get the command line arguments for starting the server
		"""

		command_args  = [self.java]
		command_args += self.settings.get('jvm_args', [])
		command_args += ['-jar', self.jar]
		command_args += self.settings.get('args', [])

		return command_args

	@property
	def admin_log(self):
		"""
		Get the admin log used for operations on the server
		"""

		return self._admin_log

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
			try:
				with open(self._settings_file, 'r') as settings_file:
					self._settings = json.load(settings_file)
			except FileNotFoundError:
				raise errors.ServerSettingsError(
					'Server settings file (mymcadmin.settings) could not be ' +
					'found.'
				)

		return self._settings

	@property
	def socket_settings(self):
		"""
		Get the socket settings for the server
		"""

		socket_props = self.settings.get('socket', {})
		if 'type' not in socket_props:
			raise errors.ServerSettingsError('Missing socket type')

		socket_type = socket_props['type']
		if socket_type != 'tcp':
			raise errors.ServerSettingsError('Invalid socket type')

		if 'port' not in socket_props:
			raise errors.ServerSettingsError('Missing socket port')

		host = socket_props.get('host', 'localhost')
		port = int(socket_props['port'])

		return (socket_type, host, port)

	def start(self):
		"""
		Start the Minecraft server
		"""

		command_args = self.command_args
		logging.info('Starting server with: {}'.format(command_args))

		# TODO(durandj): pass signals to the subprocess
		return asyncio.create_subprocess_exec(
			*command_args,
			stdin  = asyncio.subprocess.PIPE,
			stdout = asyncio.subprocess.PIPE,
			stderr = asyncio.subprocess.PIPE,
		)

	def stop(self):
		"""
		Stop the Minecraft server
		"""

		_, host, port = self.socket_settings
		with client.Client(host, port) as rpc_client:
			rpc_client.server_stop()

	def send_command(self, command):
		_, host, port = self.socket_settings

		# TODO(durandj): this needs to be repurposed as a general server command
		with client.Client(host, port) as instance_client:
			instance_client.send_command(command)

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

