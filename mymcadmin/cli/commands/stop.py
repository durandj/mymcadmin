"""
CLI commands for stopping Minecraft servers
"""

import click

from ..base import mymcadmin, cli_command, rpc_command, error, success
from ... import rpc

@mymcadmin.command()
@click.argument('server_id')
@cli_command
@rpc_command
def stop(rpc_conn, server_id):
    """
    Stop a Minecraft server
    """

    click.echo('Attempting to stop {}...'.format(server_id), nl = False)

    with rpc.RpcClient(*rpc_conn) as rpc_client:
        rpc_client.server_stop(server_id)

    success('Success')

@mymcadmin.command()
@cli_command
@rpc_command
def stop_all(rpc_conn):
    """
    Stop all Minecraft servers
    """

    with rpc.RpcClient(*rpc_conn) as rpc_client:
        result = rpc_client.server_stop_all()

        successful = result['success']
        failure    = result['failure']

    click.echo('Stopping all servers...')

    for server_id in successful:
        success('{} successfully stopped'.format(server_id))

    for server_id in failure:
        error('{} did not stop properly'.format(server_id))

