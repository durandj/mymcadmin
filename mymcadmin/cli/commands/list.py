"""
Various list type commands for the CLI
"""

import os.path

import click

from ..base import mymcadmin, cli_command, rpc_command, info
from ... import rpc, server

@mymcadmin.command()
@cli_command
@rpc_command
def list_servers(rpc_conn):
    """
    List all of the available servers
    """

    with rpc.RpcClient(*rpc_conn) as rpc_client:
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
@cli_command
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

