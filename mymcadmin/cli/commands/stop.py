"""
CLI commands for stopping Minecraft servers
"""

import click

from .. import params
from ..base import mymcadmin, error, success
from ... import server as mcserver

@mymcadmin.command()
@click.argument('server', type = params.Server())
def stop(server):
    """
    Stop a Minecraft server
    """

    stop_server(server)

@mymcadmin.command()
@click.pass_context
def stop_all(ctx):
    """
    Stop all Minecraft servers
    """

    servers = [
        mcserver.Server(srv)
        for srv in mcserver.Server.list_all(ctx.obj['config'])
    ]

    for srv in servers:
        stop_server(srv)

def stop_server(srv):
    """
    Stop a Minecraft server
    """

    click.echo('Attempting to stop {}...'.format(srv.name), nl = False)

    try:
        srv.stop()
    except Exception as ex:
        error('Failed')
        raise click.ClickException(ex)
    else:
        success('Success')

