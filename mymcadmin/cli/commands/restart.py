"""
Restart commands for Minecraft servers
"""

import click

from ..base import mymcadmin, cli_command, rpc_command, error, success
from ... import rpc

@mymcadmin.command()
@click.argument('server_id')
@cli_command
@rpc_command
def restart(rpc_conn, server_id):
    """
    Restart a Minecraft server
    """

    click.echo('Attempting to restart {}'.format(server_id), nl = False)

    with rpc.RpcClient(*rpc_conn) as rpc_client:
        rpc_client.server_restart(server_id)

    success('Success')

@mymcadmin.command()
@cli_command
@rpc_command
def restart_all(rpc_conn):
    """
    Restart all Minecraft servers
    """

    click.echo('Restarting all servers...')

    with rpc.RpcClient(*rpc_conn) as rpc_client:
        result = rpc_client.server_restart_all()

        successful = result['success']
        failure    = result['failure']

    for server_id in successful:
        success('{} successfully restarted'.format(server_id))

    for server_id in failure:
        error('{} could not restart properly'.format(server_id))

