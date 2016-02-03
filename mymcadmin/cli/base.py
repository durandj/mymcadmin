import click

from .. import config, server

@click.group()
@click.pass_context
def mymcadmin(ctx):
	"""
	MyMCAdmin CLI application
	"""

	ctx.obj = {'config': config.Config()}

