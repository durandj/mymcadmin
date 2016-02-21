"""
Minecraft Management process terminate commands
"""

import click

from ..base import mymcadmin, rpc_command, error, success
from ... import rpc

@mymcadmin.command()
@rpc_command
def shutdown(rpc_conn):
    """
    Shutdown the management server and any Minecraft servers running on it
    """

    click.echo(
        'Attempting to shutdown management server at {}:{}'.format(*rpc_conn),
        nl = False,
    )

    try:
        with rpc.RpcClient(*rpc_conn) as rpc_client:
            server_ids = rpc_client.shutdown()
    except Exception as ex:
        error('Failure')
        raise click.ClickException(ex)
    else:
        success('Success')
        for server_id in server_ids:
            success('{} successfully stopped'.format(server_id))

