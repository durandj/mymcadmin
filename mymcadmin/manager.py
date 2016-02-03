import asyncio
import asyncio.subprocess
import logging

from . import errors

class Manager(object):
	def __init__(self, server):
		logging.info('Setting up event loop')

		self.server       = server
		self.event_loop   = asyncio.get_event_loop()
		self.proc         = None
		self.network_task = None

		_, host, port = self.server.socket_settings

		logging.info('Setting up network connection')
		self.network_task = self.event_loop.create_task(
			asyncio.start_server(
				self._handle_network_connection,
				host,
				port,
				loop = self.event_loop,
			)
		)

		logging.info('Starting Minecraft server')
		self.event_loop.run_until_complete(self._handle_proc())

	def run(self):
		logging.info('Management process running')
		try:
			self.event_loop.run_forever()
		finally:
			logging.info('Shutting down management process')
			self.event_loop.close()

	async def _handle_network_connection(self, reader, writer):
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

	async def _handle_proc(self):
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

