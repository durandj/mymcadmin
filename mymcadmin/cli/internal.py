import asyncio
import click
import daemon
import daemon.pidfile
import logging
import os.path

from . import params
from .. import config, errors, manager, server, utils
from .base import mymcadmin

@mymcadmin.group()
@click.pass_context
def internal(ctx):
	"""
	For internal use only
	"""

@internal.command()
@click.pass_context
@click.argument('server', type = params.ServerParamType())
def start(ctx, server):
	if os.path.exists(server.pid_file):
		raise errors.MyMCAdminError('Server is already started')

	admin_log = open(server.admin_log, 'a')

	with daemon.DaemonContext(
			pidfile           = daemon.pidfile.PIDLockFile(server.pid_file),
			stdout            = admin_log,
			stderr            = admin_log,
			working_directory = server.path,
		):
		utils.setup_logging()

		instance_manager = manager.Manager(server)

		logging.info('Setting up event loop')
		loop = asyncio.get_event_loop()

		socket_props = server.settings.get('socket', {})
		if 'type' not in socket_props:
			raise errors.ServerSettingsError('Missing socket type')

		socket_type = socket_props['type']
		if socket_type != 'tcp':
			raise errors.ServerSettingsError('Invalid socket type')

		if 'port' not in socket_props:
			raise errors.ServerSettingsError('Missing socket port')

		host = socket_props.get('host', 'localhost')
		port = int(socket_props['port'])

		logging.info('Setting up network connection')
		routine = asyncio.start_server(
			instance_manager.handle_network_connection,
			host,
			port,
			loop = loop,
		)

		network_server = loop.run_until_complete(routine)
		instance_manager.network_future = network_server

		logging.info('Starting Minecraft server')
		loop.run_until_complete(instance_manager.handle_proc())

		logging.info('Management process running')
		loop.run_forever()

		logging.info('Shutting down management process')
		network_server.close()
		loop.run_until_complete(network_server.wait_closed())
		loop.close()

	admin_log.close()

@internal.command()
@click.pass_context
@click.argument('server', type = params.ServerParamType())
def stop(ctx, server):
	server.stop()

@internal.command()
@click.pass_context
@click.argument('server', type = params.ServerParamType())
def restart(ctx, server):
	server.restart()

