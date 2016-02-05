import click
import daemon
import daemon.pidfile
import multiprocessing
import os.path

from . import params
from .. import client, config, errors, manager, server, utils
from .base import mymcadmin

def start_server_daemon(server):
	if os.path.exists(server.pid_file):
		raise errors.MyMCAdminError('Server is already started')

	admin_log = open(server.admin_log, 'a')

	with daemon.DaemonContext(
			detach_process    = True,
			pidfile           = daemon.pidfile.PIDLockFile(server.pid_file),
			stdout            = admin_log,
			stderr            = admin_log,
			working_directory = server.path,
		):
		utils.setup_logging()

		instance_manager = manager.Manager(server)
		instance_manager.run()

	admin_log.close()

@mymcadmin.command()
@click.pass_context
def list(ctx):
	"""
	List all of the available servers
	"""

	click.echo(click.style('Available servers:', fg = 'blue'))
	for srv in server.Server.list_all(ctx.obj['config']):
		click.echo(os.path.basename(srv))

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.ServerParamType())
def start(ctx, server):
	"""
	Start a Minecraft server
	"""

	# Check if the server management process is already running
	if not os.path.exists(server.pid_file):
		proc = multiprocessing.Process(
			target = start_server_daemon,
			args = (server,),
		)

		proc.start()
		proc.join()
	else:
		# TODO(durandj): check if the minecraft server is already running
		_, host, port = server.socket_settings
		with client.Client(host, port) as rpc_client:
			rpc_client.server_start()

	click.echo(click.style('Server is starting', fg = 'green'))

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.ServerParamType())
def stop(ctx, server):
	"""
	Stop a Minecraft server
	"""

	server.stop()
	click.echo(click.style('Stopping server', fg = 'green'))

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.ServerParamType())
def restart(ctx, server):
	"""
	Restart a Minecraft server
	"""

	_, host, port = server.socket_settings
	with client.Client(host, port) as rpc_client:
		rpc_client.server_restart()

	click.echo(click.style('Server restarting', fg = 'green'))

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.ServerParamType())
def terminate(ctx, server):
	"""
	Terminate the management process for the server. This will also shutdown
	the Minecraft server
	"""

	_, host, port = server.socket_settings
	with client.Client(host, port) as rpc_client:
		rpc_client.terminate()

	click.echo(click.style('Management process terminated', fg = 'green'))

