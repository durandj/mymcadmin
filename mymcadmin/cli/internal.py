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

		logging.info('Setting up event loop')
		event_loop = asyncio.get_event_loop()

		instance_manager = manager.Manager(server, event_loop)

		logging.info('Management process running')
		try:
			event_loop.run_forever()
		finally:
			logging.info('Shutting down management process')
			event_loop.close()

	admin_log.close()

