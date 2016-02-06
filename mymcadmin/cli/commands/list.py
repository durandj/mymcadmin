import click
import os.path
import requests

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

	resp = requests.get(
		'https://launchermeta.mojang.com/mc/game/version_manifest.json'
	)

	if not resp.ok:
		error('Unable to retrieve version list')
		return

	versions     = resp.json()
	latest       = versions['latest']
	all_versions = versions['versions']

	info('Vanilla', bold = True)

	info('Latest:')
	if snapshots:
		click.echo('Snapshot: {}'.format(latest['snapshot']))
	if releases:
		click.echo('Release:  {}'.format(latest['release']))

	info('All:')
	for version in all_versions:
		version_type = version.get('type')

		if version_type == 'snapshot' and not snapshots:
			continue
		elif version_type == 'release' and not releases:
			continue
		elif version_type == 'old_beta' and not betas:
			continue
		elif version_type == 'old_alpha' and not alphas:
			continue

		click.echo(version['id'])

