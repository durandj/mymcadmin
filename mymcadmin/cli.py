import click
import os.path

from . import config, server

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

@click.group(cls = click.Group)
@click.pass_context
def mymcadmin(ctx):
	"""
	MyMCAdmin CLI application
	"""

	ctx.obj = {'config': config.Config()}

@mymcadmin.command()
@click.pass_context
def list(ctx):
	"""
	List all of the available servers
	"""

	click.echo(click.style('Available servers:', fg = 'blue'))
	for srv in server.Server.list_all(ctx.obj['config']):
		click.echo(os.path.basename(srv))

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = ServerParamType())
def start(ctx, server):
	"""
	Start a Minecraft server
	"""

	click.echo('Starting server...')
	server.start()
	click.echo(click.style('Server started', fg = 'green'))

