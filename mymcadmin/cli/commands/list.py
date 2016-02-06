import click
import os.path
import requests

from ..base import mymcadmin
from ... import server

@mymcadmin.command()
@click.pass_context
@click.option(
	'--snapshots/--no-snapshots',
	default = True,
	help = 'Include snapshots')
def list_server_versions(ctx, snapshots):
	"""
	List possible server downloads
	"""

	resp = requests.get(
		'https://launchermeta.mojang.com/mc/game/version_manifest.json'
	)

	if not resp.ok:
		click.echo(click.style('Unable to retrieve version list', fg = 'red'))
		return

	versions     = resp.json()
	latest       = versions['latest']
	all_versions = versions['versions']

	click.echo(click.style('Vanilla', fg = 'blue', bold = True))

	click.echo(click.style('Latest:', fg = 'blue'))
	if snapshots:
		click.echo('Snapshot: {}'.format(latest['snapshot']))
	click.echo('Release:  {}'.format(latest['release']))

	click.echo(click.style('All', fg = 'blue'))
	for version in all_versions:
		if version.get('type') == 'snapshot' and not snapshots:
			continue

		click.echo(version['id'])

@mymcadmin.command()
@click.pass_context
def list_servers(ctx):
	"""
	List all of the available servers
	"""

	click.echo(click.style('Available servers:', fg = 'blue'))
	for srv in server.Server.list_all(ctx.obj['config']):
		click.echo(os.path.basename(srv))

