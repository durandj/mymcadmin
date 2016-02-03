import asyncio
import asyncio.subprocess
import logging

from . import errors

class Manager(object):
	def __init__(self, server, event_loop):
		self.server       = server
		self.event_loop   = event_loop
		self.proc         = None
		self.network_task = None

		socket_props = self.server.settings.get('socket', {})
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
		self.network_task = self.event_loop.create_task(
			asyncio.start_server(
				self.handle_network_connection,
				host,
				port,
				loop = self.event_loop,
			)
		)

		logging.info('Starting Minecraft server')
		self.event_loop.run_until_complete(self.handle_proc())

	async def handle_network_connection(self, reader, writer):
		data    = await reader.readline()
		message = data.decode()

		address = writer.get_extra_info('peername')
		logging.info(
			'Recieved "{}" from {}'.format(
				message,
				address,
			)
		)

		await self.proc.communicate(data)

		writer.close()

	async def handle_proc(self):
		proc_future = asyncio.Future()
		proc_future.add_done_callback(self._handle_proc_terminated)

		create = self.server.start(
			stdin  = asyncio.subprocess.PIPE,
			stdout = asyncio.subprocess.PIPE,
			stderr = asyncio.subprocess.PIPE,
		)

		self.proc = await create

		await self.proc.wait()

		proc_future.set_result(self.proc.returncode)

	def _handle_proc_terminated(self, future):
		self.event_loop.stop()

