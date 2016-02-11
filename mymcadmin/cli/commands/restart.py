import click

from .. import params
from ..base import mymcadmin, error, success
from ... import rpc, server as mcserver

@mymcadmin.command()
@click.argument('server', type = params.Server())
def restart(server):
    """
    Restart a Minecraft server
    """

    restart_server(server)

@mymcadmin.command()
@click.pass_context
def restart_all(ctx):
    """
    Restart all Minecraft servers
    """

    servers = [
        mcserver.Server(srv)
        for srv in mcserver.Server.list_all(ctx.obj['config'])
    ]

    for srv in servers:
        restart_server(srv)

def restart_server(srv):
    click.echo('Attempting to restart {}'.format(srv.name), nl = False)

    try:
        _, host, port = srv.socket_settings
        with rpc.RpcClient(host, port) as rpc_client:
            rpc_client.server_restart()
    except Exception as ex:
        error('Failure')
        raise click.ClickException(ex)
    else:
        success('Success')

