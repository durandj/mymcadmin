import click

from .. import params
from ..base import mymcadmin
from ... import rpc, server

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.Server())
def stop(ctx, srv):
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
		click.echo(click.style('Failed', fg = 'red'))
		click.echo(click.style(str(e), fg = 'yellow'))
	else:
		click.echo(click.style('Success', fg = 'green'))

def restart_server(srv):
	click.echo('Attempting to restart {}'.format(srv.name), nl = False)

	try:
		_, host, port = srv.socket_settings
		with rpc.RpcClient(host, port) as rpc_client:
			rpc_client.server_restart()
	except Exception as e:
		click.echo(click.style('Failure', fg = 'red'))
		click.echo(click.style(str(e), color = 'yellow'))
	else:
		click.echo(click.style('Success', fg = 'green'))

