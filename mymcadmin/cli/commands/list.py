import click
import os.path

from ..base import mymcadmin
from ... import server

@mymcadmin.command()
@click.pass_context
def list_server_downloads(ctx):
	"""
	List possible server downloads
	"""

@mymcadmin.command()
@click.pass_context
def list_servers(ctx):
	"""
	List all of the available servers
	"""

	click.echo(click.style('Available servers:', fg = 'blue'))
	for srv in server.Server.list_all(ctx.obj['config']):
		click.echo(os.path.basename(srv))

