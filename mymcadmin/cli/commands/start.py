"""
Start commands
"""

import multiprocessing
import grp
import os
import os.path
import pwd

import click
import daemon
import daemon.pidfile

from .. import params
from ..base import mymcadmin, error, success
from ... import (
    errors,
    manager,
    rpc,
    utils,
)

@mymcadmin.command()
@click.argument('server_id')
@click.option('--host', default = None, help = 'The host to connect to')
@click.option('--port', default = None, help = 'The port to connect to')
@click.pass_context
def start(ctx, server_id, host, port):
    """
    Start a Minecraft server
    """

    rpc_config = ctx.obj['config'].rpc or {}

    if not host:
        host = rpc_config.get('host', 'localhost')

    if not port:
        port = rpc_config.get('port', 2323)

    click.echo('Starting {}...'.format(server_id), nl = False)

    try:
        with rpc.RpcClient(host, port) as rpc_client:
            rpc_client.server_start(server_id)
    except Exception as ex:
        error('Failure')
        raise click.ClickException(ex)
    else:
        success('Success')

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
        host = rpc_config.get('host', 'localhost')

    if not port:
        port = rpc_config.get('port', 2323)

    click.echo('Attempting to start all servers...')

    try:
        with rpc.RpcClient(host, port) as rpc_client:
            result = rpc_client.server_start_all()

            successful = result['success']
            failure    = result['failure']
    except Exception as ex:
        error('Failure')
        raise click.ClickException(ex)
    else:
        for server_id in successful:
            success('{} successfully started'.format(server_id))

        for server_id in failure:
            error('{} did not start properly'.format(server_id))

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

    daemon_config = ctx.obj['config'].daemon or {}

    def _get_option(name, default, convert = None):
        if kwargs[name] is not None:
            return kwargs[name]

        value = daemon_config.get(name, default)
        if convert:
            try:
                return convert(value)
            except Exception:
                raise click.ClickException(
                    'Configuration value is not valid. {}: {}'.format(name, value)
                )

        return value

    def _convert_user(user):
        if isinstance(user, int):
            pwd.getpwuid(user)

            return user
        else:
            return pwd.getpwnam(user).pw_uid

    def _convert_group(group):
        if isinstance(group, int):
            grp.getgrgid(group)

            return group
        else:
            return grp.getgrnam(group).gr_gid

    host  = _get_option('host', 'localhost')
    port  = _get_option('port', 2323)
    user  = _get_option('user', os.getuid(), convert = _convert_user)
    group = _get_option('group', os.getgid(), convert = _convert_group)

    root = _get_option(
        'root',
        os.path.join(utils.get_user_home(user), 'mymcadmin'),
    )

    pid = _get_option('pid', os.path.join(root, 'daemon.pid'))
    log = _get_option('log', os.path.join(root, 'mymcadmin.log'))

    click.echo(
        'Starting daemon as {} {} on {}:{}...'.format(
            user,
            group,
            host,
            port,
        ),
        nl = False,
    )

    try:
        if os.path.exists(pid):
            raise errors.ManagerError('Management daemon is already started')

        proc = multiprocessing.Process(
            target = start_management_daemon,
            kwargs = {
                'host':  host,
                'port':  port,
                'user':  user,
                'group': group,
                'root':  root,
                'pid':   pid,
                'log':   log,
            },
        )

        proc.start()
        proc.join()
    except Exception as ex:
        error('Failure')
        raise click.ClickException(str(ex))
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

