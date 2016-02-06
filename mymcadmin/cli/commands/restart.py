import click

from .. import params
from ..base import mymcadmin, error, success, warn
from ... import rpc, server

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.Server())
def restart(ctx, server):
	"""
	Restart a Minecraft server
	"""

	restart_server(server)

@mymcadmin.command()
@click.pass_context
def restart_all(ctx):
	"""
	Restart all Minecraft servers
	"""

	servers = [
		server.Server(srv)
		for srv in server.Server.list_all(ctx.obj['config'])
	]

	for srv in servers:
		restart_server(srv)

def restart_server(srv):
	click.echo('Attempting to restart {}'.format(srv.name), nl = False)

	try:
		_, host, port = srv.socket_settings
		with rpc.RpcClient(host, port) as rpc_client:
			rpc_client.server_restart()
	except Exception as e:
		error('Failure')
		warn(str(e))
	else:
		success('Success')

