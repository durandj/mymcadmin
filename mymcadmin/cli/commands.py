import click
import daemon
import daemon.pidfile
import multiprocessing
import os.path

from . import params
from .. import client, config, errors, manager, server, utils

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

	start_server(server)

@mymcadmin.command()
@click.pass_context
def start_all(ctx):
	"""
	Start all Minecraft servers
	"""

	servers = [
		server.Server(srv)
		for srv in server.Server.list_all(ctx.obj['config'])
	]

	for srv in servers:
		start_server(srv)

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.ServerParamType())
def stop(ctx, server):
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
		server.Server(srv)
		for srv in server.Server.list_all(ctx.obj['config'])
	]

	for srv in servers:
		stop_server(srv)

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.ServerParamType())
def restart(ctx, server):
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
		server.Server(srv)
		for srv in server.Server.list_all(ctx.obj['config'])
	]

	for srv in servers:
		restart_server(srv)

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.ServerParamType())
def terminate(ctx, server):
	"""
	Terminate the management process for the server. This will also shutdown
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
		server.Server(srv)
		for srv in server.Server.list_all(ctx.obj['config'])
	]

	for srv in servers:
		terminate_server(srv)

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

def start_server(server):
	click.echo('Attempting to start {}...'.format(server.name), nl = False)

	try:
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
	except Exception as e:
		click.echo(click.style('Failure', fg = 'red'))
		click.echo(click.style(str(e), color = 'yellow'))
	else:
		click.echo(click.style('Success', fg = 'green'))

def stop_server(srv):
	click.echo('Attempting to stop {}...'.format(srv.name), nl = False)

	try:
		srv.stop()
	except Exception as e:
		click.echo(click.style('Failed', fg = 'red'))
		click.echo(click.style(str(e), fg = 'yellow'))
	else:
		click.echo(click.style('Success', fg = 'green'))

def restart_server(srv):
	click.echo('Attempting to restart {}'.format(srv.name), nl = False)

	try:
		_, host, port = srv.socket_settings
		with client.Client(host, port) as rpc_client:
			rpc_client.server_restart()
	except Exception as e:
		click.echo(click.style('Failure', fg = 'red'))
		click.echo(click.style(str(e), color = 'yellow'))
	else:
		click.echo(click.style('Success', fg = 'green'))

def terminate_server(srv):
	click.echo('Attempting to terminate {}'.format(srv), nl = False)

	try:
		_, host, port = srv.socket_settings
		with client.Client(host, port) as rpc_client:
			rpc_client.terminate()
	except Exception as e:
		click.echo(click.style('Failure', fg = 'red'))
		click.echo(click.style(str(e), color = 'yellow'))
	else:
		click.echo(click.style('Success', fg = 'green'))

