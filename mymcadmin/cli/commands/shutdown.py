"""
Minecraft Management process terminate commands
"""

import click

from ..base import mymcadmin, error, success
from ... import rpc

@mymcadmin.command()
@click.option('--host', default = None, help = 'The host to connect to')
@click.option(
    '--port',
    type    = click.INT,
    default = None,
    help    = 'The port to connect to')
@click.pass_context
def shutdown(ctx, host, port):
    """
    Shutdown the management server and any Minecraft servers running on it
    """

    rpc_config = ctx.obj['config'].rpc or {}

    if host is None:
        host = rpc_config.get('host', 'localhost')

    if port is None:
        port = rpc_config.get('port', 2323)

    click.echo(
        'Attempting to shutdown management server at {}:{}'.format(host, port),
        nl = False,
    )

    try:
        with rpc.RpcClient(host, port) as rpc_client:
            server_ids = rpc_client.shutdown()
    except Exception as ex:
        error('Failure')
        raise click.ClickException(ex)
    else:
        success('Success')
        for server_id in server_ids:
            success('{} successfully stopped'.format(server_id))

