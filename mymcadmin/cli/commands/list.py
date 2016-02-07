import click
import os.path

from ..base import mymcadmin, error, info
from ... import server

@mymcadmin.command()
@click.pass_context
def list_servers(ctx):
	"""
	List all of the available servers
	"""

	info('Available servers:')
	for srv in server.Server.list_all(ctx.obj['config']):
		click.echo(os.path.basename(srv))

@mymcadmin.command()
@click.pass_context
@click.option(
	'--snapshots/--no-snapshots',
	default = True,
	help    = 'Include snapshots')
@click.option(
	'--releases/--no-releases',
	default = True,
	help    = 'Include releases')
@click.option(
	'--betas/--no-betas',
	default = True,
	help    = 'Include betas')
@click.option(
	'--alphas/--no-alphas',
	default = True,
	help    = 'Include alphas')
def list_versions(ctx, snapshots, releases, betas, alphas):
	"""
	List possible server download versions
	"""

	versions = server.Server.list_versions(
		snapshots = snapshots,
		releases  = releases,
		betas     = betas,
		alphas    = alphas
	)

	latest       = versions['latest']
	all_versions = versions['versions']

	info('Vanilla', bold = True)

	info('Latest:')
	click.echo('Snapshot: {}'.format(latest.get('snapshot', '')))
	click.echo('Release:  {}'.format(latest.get('release', '')))

	info('All:')
	for version in all_versions:
		click.echo(version['id'])

