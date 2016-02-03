import click
import os.path

from .. import server

class ServerParamType(click.ParamType):
	name = 'server'

	def __init__(self, exists = True):
		self.exists = exists

	def convert(self, value, param, ctx):
		config      = ctx.obj['config']
		server_path = os.path.join(config.instance_path, value)

		if self.exists and not os.path.exists(server_path):
			self.fail('Server does not exist')

		return server.Server(server_path)

