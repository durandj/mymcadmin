"""
Various list type commands for the CLI
"""

import os.path

import click

from ..base import mymcadmin, info
from ... import rpc, server

@mymcadmin.command()
@click.option('--host', default = None, help = 'The host to connect to')
@click.option(
    '--port',
    type = click.INT,
    default = None,
    help = 'The port to connect to')
@click.pass_context
def list_servers(ctx, host, port):
    """
    List all of the available servers
    """

    rpc_config = ctx.obj['config'].rpc or {}

    if host is None:
        host = rpc_config.get('host', 'localhost')

    if port is None:
        port = rpc_config.get('port', 2323)

    with rpc.RpcClient(host, port) as rpc_client:
        server_ids = rpc_client.list_servers()

    info('Available servers:')
    for srv in server_ids:
        click.echo(os.path.basename(srv))

@mymcadmin.command()
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
def list_versions(snapshots, releases, betas, alphas):
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

