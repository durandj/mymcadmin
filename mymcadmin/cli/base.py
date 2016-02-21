"""
Base command handling
"""

import functools

import click

from .. import config

@click.group()
@click.pass_context
@click.option(
    '--conf',
    type    = click.Path(dir_okay = False, exists = True),
    default = None,
    help    = 'Path to a configuration file to use')
def mymcadmin(ctx, conf):
    """
    MyMCAdmin CLI application
    """

    ctx.obj = {'config': config.Config(config_file = conf)}

def rpc_command(command):
    """
    Sets up a command to connect to the server via RPC
    """

    @click.option('--host', default = None, help = 'The host to connect to')
    @click.option(
        '--port',
        type    = click.INT,
        default = None,
        help    = 'The port to connect to')
    @click.pass_context
    def _wrapper(ctx, host, port, *args, **kwargs):
        rpc_config = ctx.obj['config'].rpc or {}

        if host is None:
            host = rpc_config.get('host', 'localhost')

        if port is None:
            port = rpc_config.get('port', 2323)

        kwargs['rpc_conn'] = (host, port)

        return ctx.invoke(command, *args, **kwargs)

    return functools.update_wrapper(_wrapper, command)

def success(message, **formatting):
    """
    Return a success message to the command line
    """

    click.secho(message, fg = 'green', **formatting)

def info(message, **formatting):
    """
    Return an info message to the command line
    """

    click.secho(message, fg = 'blue', **formatting)

def warn(message, **formatting):
    """
    Return a warning message to the command line
    """

    click.secho(message, fg = 'yellow', **formatting)

def error(message, **formatting):
    """
    Return an error message to the command line
    """

    click.secho(message, fg = 'red', **formatting)

