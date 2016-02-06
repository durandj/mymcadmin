import click

from .. import config

@click.group()
@click.pass_context
@click.option(
	'--conf',
	type    = click.Path(dir_okay = False, exists = True),
	default = None,
	help    = 'Path to a configuration file to use')
def mymcadmin(ctx, conf):
	"""
	MyMCAdmin CLI application
	"""

	ctx.obj = {'config': config.Config(config_file = conf)}

def success(message, **formatting):
	click.secho(message, fg = 'green', **formatting)

def info(message, **formatting):
	click.secho(message, fg = 'blue', **formatting)

def warn(message, **formatting):
	click.secho(message, fg = 'yellow', **formatting)

def error(message, **formatting):
	click.secho(message, fg = 'red', **formatting)

