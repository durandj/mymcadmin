"""
Minecraft Management process terminate commands
"""

import click

from .. import params
from ..base import mymcadmin, error, success
from ... import rpc, server as mcserver

@mymcadmin.command()
@click.argument('server', type = params.Server())
def terminate(server):
    """
    Terminate the management process for the server. This will aso shutdown
    the Minecraft server
    """

    terminate_server(server)

@mymcadmin.command()
@click.pass_context
def terminate_all(ctx):
    """
    Terminate all Minecraft servers
    """

    servers = [
        mcserver.Server(srv)
        for srv in mcserver.Server.list_all(ctx.obj['config'])
    ]

    for srv in servers:
        terminate_server(srv)

def terminate_server(srv):
    """
    Terminate a server's management process
    """

    click.echo('Attempting to terminate {}'.format(srv), nl = False)

    try:
        _, host, port = srv.socket_settings
        with rpc.RpcClient(host, port) as rpc_client:
            rpc_client.terminate()
    except Exception as ex:
        error('Failure')
        raise click.ClickException(ex)
    else:
        success('Success')

