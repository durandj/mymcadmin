"""
Restart commands for Minecraft servers
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
def restart(ctx, server_id, host, port):
    """
    Restart a Minecraft server
    """

    rpc_config = ctx.obj['config'].rpc or {}

    if host is None:
        host = rpc_config.get('host', 'localhost')

    if port is None:
        port = rpc_config.get('port', 2323)

    click.echo('Attempting to restart {}'.format(server_id), nl = False)

    try:
        with rpc.RpcClient(host, port) as rpc_client:
            rpc_client.server_restart(server_id)
    except Exception as ex:
        error('Failure')
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
def restart_all(ctx, host, port):
    """
    Restart all Minecraft servers
    """

    rpc_config = ctx.obj['config'].rpc or {}

    if host is None:
        host = rpc_config.get('host', 'localhost')

    if port is None:
        port = rpc_config.get('port', 2323)

    click.echo('Restarting all servers...')

    try:
        with rpc.RpcClient(host, port) as rpc_client:
            result = rpc_client.server_restart_all()

            successful = result['success']
            failure    = result['failure']
    except Exception as ex:
        error('Failure')
        raise click.ClickException(ex)
    else:
        for server_id in successful:
            success('{} successfully restarted'.format(server_id))

        for server_id in failure:
            error('{} could not restart properly'.format(server_id))

