"""
Restart commands for Minecraft servers
"""

import click

from ..base import mymcadmin, rpc_command, error, success
from ... import rpc

@mymcadmin.command()
@click.argument('server_id')
@rpc_command
def restart(rpc_conn, server_id):
    """
    Restart a Minecraft server
    """

    click.echo('Attempting to restart {}'.format(server_id), nl = False)

    try:
        with rpc.RpcClient(*rpc_conn) as rpc_client:
            rpc_client.server_restart(server_id)
    except Exception as ex:
        error('Failure')
        raise click.ClickException(ex)
    else:
        success('Success')

@mymcadmin.command()
@rpc_command
def restart_all(rpc_conn):
    """
    Restart all Minecraft servers
    """

    click.echo('Restarting all servers...')

    try:
        with rpc.RpcClient(*rpc_conn) as rpc_client:
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

