import click

from .. import params
from ..base import mymcadmin
from ... import rpc, server

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.Server())
def terminate(ctx, srv):
	"""
	Terminate the management process for the server. This will aso shutdown
	the Minecraft server
	"""

	terminate_server(srv)

@mymcadmin.command()
@click.pass_context
def terminate_all(ctx):
	"""
	Terminate all Minecraft servers
	"""

	servers = [
		server.Server(srv)
		for srv in server.Server.list_all(ctx.obj['config'])
	]

	for srv in servers:
		terminate_server(srv)

def terminate_server(srv):
	click.echo('Attempting to terminate {}'.format(srv), nl = False)

	try:
		_, host, port = srv.socket_settings
		with rpc.RpcClient(host, port) as rpc_client:
			rpc_client.terminate()
	except Exception as e:
		click.echo(click.style('Failure', fg = 'red'))
		click.echo(click.style(str(e), color = 'yellow'))
	else:
		click.echo(click.style('Success', fg = 'green'))
