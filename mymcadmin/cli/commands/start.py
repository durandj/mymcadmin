import click
import daemon
import daemon.pidfile
import multiprocessing
import os.path

from .. import params
from ..base import mymcadmin, error, success, warn
from ... import (
	errors,
	manager,
	rpc,
	server,
	utils,
)

@mymcadmin.command()
@click.pass_context
@click.argument('server', type = params.Server())
@click.option(
	'--user',
	type    = params.User(),
	default = None,
	help    = 'The user to run the server as')
@click.option(
	'--group',
	type    = params.Group(),
	default = None,
	help    = 'The group to run the server as')
def start(ctx, server, user, group):
	"""
	Start a Minecraft server
	"""

	start_server(server, user, group)

@mymcadmin.command()
@click.pass_context
@click.option(
	'--user',
	type    = params.User(),
	default = None,
	help    = 'The user to run the servers as')
@click.option(
	'--group',
	type    = params.Group(),
	default = None,
	help    = 'The group to run the servers as')
def start_all(ctx, user, group):
	"""
	Start all Minecraft servers
	"""

	servers = [
		server.Server(srv)
		for srv in server.Server.list_all(ctx.obj['config'])
	]

	for srv in servers:
		start_server(srv, user, group)

def start_server_daemon(server, user, group):
	if os.path.exists(server.pid_file):
		raise errors.MyMCAdminError('Server is already started')

	admin_log = open(server.admin_log, 'a')

	with daemon.DaemonContext(
			detach_process    = True,
			gid               = group,
			pidfile           = daemon.pidfile.PIDLockFile(server.pid_file),
			stdout            = admin_log,
			stderr            = admin_log,
			uid               = user,
			working_directory = server.path,
		):
		utils.setup_logging()

		instance_manager = manager.Manager(server)
		instance_manager.run()

	admin_log.close()

def start_server(server, user, group):
	click.echo(
		'Attempting to start {} as ({}, {})...'.format(
			server.name,
			user or 'default',
			group or 'default',
		),
		nl = False,
	)

	try:
		# Check if the server management process is already running
		if not os.path.exists(server.pid_file):
			proc = multiprocessing.Process(
				target = start_server_daemon,
				args = (server, user, group),
			)

			proc.start()
			proc.join()
		else:
			# TODO(durandj): check if the minecraft server is already running
			_, host, port = server.socket_settings
			with rpc.RpcClient(host, port) as rpc_client:
				rpc_client.server_start()
	except Exception as e:
		error('Failure')
		raise click.ClickException(e)
	else:
		success('Success')

