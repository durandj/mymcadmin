"""
CLI commands for stopping Minecraft servers
"""

import click

from ..base import mymcadmin, error, success
from ... import rpc

@mymcadmin.command()
@click.argument('server_id')
@click.option('--host', default = None, help = 'The host to connect to')
@click.option(
    '--port',
    type    = click.INT,
    default = None,
    help    = 'The port to connect to')
@click.pass_context
def stop(ctx, server_id, host, port):
    """
    Stop a Minecraft server
    """

    rpc_config = ctx.obj['config'].rpc or {}

    if host is None:
        host = rpc_config.get('host', 'localhost')

    if port is None:
        port = rpc_config.get('port', 2323)

    click.echo('Attempting to stop {}...'.format(server_id), nl = False)

    try:
        with rpc.RpcClient(host, port) as rpc_client:
            rpc_client.server_stop(server_id)
    except Exception as ex:
        error('Failed')
        raise click.ClickException(ex)
    else:
        success('Success')

@mymcadmin.command()
@click.option('--host', default = None, help = 'The host to connect to')
@click.option(
    '--port',
    type    = click.INT,
    default = None,
    help    = 'The port to connect to')
@click.pass_context
def stop_all(ctx, host, port):
    """
    Stop all Minecraft servers
    """

    rpc_config = ctx.obj['config'].rpc or {}

    if host is None:
        host = rpc_config.get('host', 'localhost')

    if port is None:
        port = rpc_config.get('port', 2323)

    try:
        with rpc.RpcClient(host, port) as rpc_client:
            server_ids = rpc_client.server_stop_all()
    except Exception as ex:
        error('Failed')
        raise click.ClickException(ex)
    else:
        click.echo('Stopping all servers...')

        # TODO(durandj): a list of failures would be helpful too
        for server_id in server_ids:
            success('{} successfully stopped'.format(server_id))

