import click

from .. import params
from ..base import mymcadmin, error, success, warn
from ... import rpc, server

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.Server())
def stop(ctx, server):
	"""
	Stop a Minecraft server
	"""

	stop_server(server)

@mymcadmin.command()
@click.pass_context
def stop_all(ctx):
	"""
	Stop all Minecraft servers
	"""

	servers = [
		server.Server(srv)
		for srv in server.Server.list_all(ctx.obj['config'])
	]

	for srv in servers:
		stop_server(srv)

def stop_server(srv):
	click.echo('Attempting to stop {}...'.format(srv.name), nl = False)

	try:
		srv.stop()
	except Exception as e:
		error('Failed')
		warn(str(e))
	else:
		success('Success')

