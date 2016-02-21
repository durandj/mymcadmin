"""
Commands for creating a server
"""

import click

from ..base import mymcadmin, success, error, warn
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
@click.option('--host', default = None, help = 'The host to connect to')
@click.option(
    '--port',
    type    = click.INT,
    default = None,
    help    = 'The port to connect to')
@click.pass_context
def create(ctx, server_id, version, forge, forge_version, host, port):
    """
    Creates a Minecraft server instance
    """

    rpc_config = ctx.obj['config'].rpc or {}

    if host is None:
        host = rpc_config.get('host', 'localhost')

    if port is None:
        port = rpc_config.get('port', 2323)

    warn('By creating a server you are agreeing to Mojang\'s EULA.')
    warn('https://account.mojang.com/documents/minecraft_eula', underline = True)
    click.confirm('Do you agree to the EULA?', abort = True)

    click.echo('Attempting to create server {}'.format(server_id))

    try:
        with rpc.RpcClient(host, port) as rpc_client:
            kwargs = {}
            if forge:
                kwargs['forge'] = forge_version or forge

            rpc_client.server_create(server_id, version, **kwargs)
    except Exception as ex:
        error('Failed')
        raise click.ClickException(ex)
    else:
        success('Server {} successfully created'.format(server_id))

