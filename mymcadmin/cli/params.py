import click
import grp
import os.path
import pwd

from .. import server

class Server(click.ParamType):
	name = 'server'

	def __init__(self, exists = True):
		self.exists = exists

	def convert(self, value, param, ctx):
		config      = ctx.obj['config']
		server_path = os.path.join(config.instance_path, value)

		if self.exists and not os.path.exists(server_path):
			self.fail('Server does not exist')

		return server.Server(server_path)

class User(click.ParamType):
	name = 'user'

	def convert(self, value, param, ctx):
		try:
			if isinstance(value, int):
				# This call should fail if the UID doesn't exist
				pwd.getpwuid(value)
				return value
			else:
				return pwd.getpwnam(value).pw_uid
		except KeyError:
			self.fail('User {} does not exist'.format(value))

class Group(click.ParamType):
	name = 'group'

	def convert(self, value, param, ctx):
		try:
			if isinstance(value, int):
				# This call should fail if the GID doesn't exist
				grp.getgrgid(value)
				return value
			else:
				return grp.getgrnam(value).gr_gid
		except (KeyError, OverflowError):
			self.fail('Group {} does not exist'.format(value))

