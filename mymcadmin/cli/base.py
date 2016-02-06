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


