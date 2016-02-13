"""
Start commands
"""

import multiprocessing
import os
import os.path

import click
import daemon
import daemon.pidfile

from .. import params
from ..base import mymcadmin, error, success
from ... import (
    errors,
    manager,
    rpc,
    server as mcserver,
    utils,
)

@mymcadmin.command()
@click.argument('server', type = params.Server())
@click.option('--host', default = None, help = 'The host to connect to')
@click.option('--port', default = None, help = 'The port to connect to')
@click.pass_context
def start(ctx, server, host, port):
    """
    Start a Minecraft server
    """

    rpc_config = ctx.obj['config'].rpc or {}

    if not host:
        host = rpc_config.get('host')

    if not port:
        port = rpc_config.get('port')

    start_server(server, host, port)

@mymcadmin.command()
@click.option('--host', default = None, help = 'The host to connect to')
@click.option('--port', default = None, help = 'The port to connect to')
@click.pass_context
def start_all(ctx, host, port):
    """
    Start all Minecraft servers
    """

    rpc_config = ctx.obj['config'].rpc or {}

    if not host:
        host = rpc_config.get('host')

    if not port:
        port = rpc_config.get('port')

    servers = [
        mcserver.Server(srv)
        for srv in mcserver.Server.list_all(ctx.obj['config'])
    ]

    for srv in servers:
        start_server(srv, host, port)

@mymcadmin.command()
@click.option('--host', default = None, help = 'The host to listen on')
@click.option(
    '--port',
    type    = click.INT,
    default = None,
    help    = 'The port to listen on')
@click.option(
    '--user',
    type    = params.User(),
    default = None,
    help    = 'The user to run as')
@click.option(
    '--group',
    type    = params.Group(),
    default = None,
    help    = 'The group to run as')
@click.option(
    '--root',
    type    = click.Path(file_okay = False),
    default = None,
    help    = 'The location where instances are stored')
@click.option(
    '--pid',
    type    = click.Path(dir_okay = False),
    default = None,
    help    = 'The location of the PID file')
@click.option(
    '--log',
    type    = click.Path(dir_okay = False),
    default = None,
    help    = 'The log file to write to')
@click.pass_context
def start_daemon(ctx, **kwargs):
    """
    Start management daemon
    """

    config        = ctx.obj['config']
    daemon_config = config.daemon or {}

    def _get_option(name, default):
        if kwargs[name] is not None:
            return kwargs[name]

        return daemon_config.get(name, default)

    host  = _get_option('host', 'localhost')
    port  = _get_option('port', 2323)
    user  = _get_option('user', os.getuid())
    group = _get_option('group', os.getgid())

    root = _get_option(
        'root',
        os.path.join(utils.get_user_home(user), 'mymcadmin'),
    )

    pid = _get_option('pid', os.path.join(root, 'daemon.pid'))
    log = _get_option('log', os.path.join(root, 'mymcadmin.log'))

    click.echo('Starting daemon...', nl = False)

    try:
        if os.path.exists(pid):
            raise errors.ManagerError('Management daemon is already started')

        proc = multiprocessing.Process(
            target = start_management_daemon,
            args   = (host, port, user, group, root, pid, log),
        )

        proc.start()
        proc.join()
    except Exception as ex:
        error('Failure')
        raise click.ClickException(str(ex))
    else:
        success('Success')

def start_server(server, host, port):
    """
    Start a Minecraft server
    """

    click.echo('Starting {}...'.format(server.name), nl = False)

    if not host:
        host = 'localhost'

    if not port:
        port = 2323

    try:
        with rpc.RpcClient(host, port) as rpc_client:
            rpc_client.server_start(server.name)
    except Exception as ex:
        error('Failure')
        raise click.ClickException(ex)
    else:
        success('Success')

def start_management_daemon(**kwargs):
    """
    Start the management daemon
    """

    daemon_log = open(kwargs['log'], 'a')

    with daemon.DaemonContext(
        detach_process    = True,
        gid               = kwargs['group'],
        pidfile           = daemon.pidfile.PIDLockFile(kwargs['pid']),
        stdout            = daemon_log,
        stderr            = daemon_log,
        uid               = kwargs['user'],
        working_directory = kwargs['root'],
        ):
        utils.setup_logging()

        proc = manager.Manager(
            kwargs['host'],
            kwargs['port'],
            kwargs['root'],
        )
        proc.run()

    daemon_log.close()

