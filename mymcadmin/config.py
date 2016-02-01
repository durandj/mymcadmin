import json
import os.path

import mymcadmin.errors

class Config(object):
	"""
	MyMCAdmin's configuration file for controlling things like where server
	instances are stored. Config files are stored in each user's home directory
	as ".mymcadminrc".
	"""

	CONFIG_FILE = os.path.expanduser(
		os.path.expandvars(
			os.path.join('~', '.mymcadminrc')
		)
	)

	def __init__(self):
		with open(Config.CONFIG_FILE, 'r') as config:
			self._config = json.load(config)

	def __getattr__(self, name):
		if name not in self._config:
			raise mymcadmin.errors.ConfigurationError(
				'No option "{}" in configuration file',
				name,
			)

		return self._config[name]

