import click

from ..base import mymcadmin

@mymcadmin.command()
@click.pass_context
@click.argument('name')
def create_server(ctx, name):
	# TODO(durandj): get the server version
	# TODO(durandj): check if the server exists already
	# TODO(durandj): check if the version is valid
	# TODO(durandj): create the server

	pass

