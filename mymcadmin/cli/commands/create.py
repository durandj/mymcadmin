"""
Commands for creating a server
"""

import click

from ..base import mymcadmin, rpc_command, success, error, warn
from ... import rpc

@mymcadmin.command()
@click.argument('server_id')
@click.option(
    '--version',
    default = None,
    help    = 'Minecraft version, defaults to latest release')
@click.option(
    '--forge/--no-forge',
    help = 'Include Forge with the new server')
@click.option(
    '--forge_version',
    default = None,
    help    = 'The specfic Forge version to get')
@rpc_command
def create(rpc_conn, server_id, version, forge, forge_version):
    """
    Creates a Minecraft server instance
    """

    warn('By creating a server you are agreeing to Mojang\'s EULA.')
    warn('https://account.mojang.com/documents/minecraft_eula', underline = True)
    click.confirm('Do you agree to the EULA?', abort = True)

    click.echo('Attempting to create server {}'.format(server_id))

    try:
        with rpc.RpcClient(*rpc_conn) as rpc_client:
            rpc_kwargs = {}
            if forge:
                rpc_kwargs['forge'] = forge_version or forge

            rpc_client.server_create(server_id, version, **rpc_kwargs)
    except Exception as ex:
        error('Failed')
        raise click.ClickException(ex)
    else:
        success('Server {} successfully created'.format(server_id))

