"""
Commands for creating a server
"""

import click

from ..base import mymcadmin

@mymcadmin.command()
@click.pass_context
@click.argument('name')
@click.option(
    '--version',
    default = None,
    help    = 'Minecraft version, defaults to latest release')
def create_server(ctx, name, version):
    """
    Creates a Minecraft server instance
    """

    # TODO(durandj): get the server version
    # TODO(durandj): check if the server exists already
    # TODO(durandj): check if the version is valid
    # TODO(durandj): create the server

    pass

