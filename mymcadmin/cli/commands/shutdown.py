"""
Minecraft Management process terminate commands
"""

import click

from ..base import mymcadmin, cli_command, rpc_command, success
from ... import rpc

@mymcadmin.command()
@cli_command
@rpc_command
def shutdown(rpc_conn):
    """
    Shutdown the management server and any Minecraft servers running on it
    """

    click.echo(
        'Attempting to shutdown management server at {}:{}'.format(*rpc_conn),
        nl = False,
    )

    with rpc.RpcClient(*rpc_conn) as rpc_client:
        server_ids = rpc_client.shutdown()

    success('Success')
    for server_id in server_ids:
        success('{} successfully stopped'.format(server_id))

