import asyncio
import asyncio.subprocess
import logging

from . import errors, rpc

class Manager(object):
	def __init__(self, server):
		logging.info('Setting up event loop')

		self.server         = server
		self.event_loop     = asyncio.get_event_loop()
		self.proc           = None
		self.network_task   = None
		self.rpc_dispatcher = rpc.Dispatcher()

		self._setup_rpc_handlers()

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

	def _setup_rpc_handlers(self):
		logging.info('Setting up JSON RPC handlers')

		self.rpc_dispatcher.add_method(self._rpc_command_stop, name = 'stop')

	async def _rpc_command_stop(self, **kwargs):
		logging.info('Sending stop command to server')

		await self.proc.communicate('stop'.encode())

		return 'stopping server'

	async def _handle_rpc(self, rpc_data):
		return await rpc.JsonRpcResponseManager.handle(
			rpc_data,
			self.rpc_dispatcher,
		)

	async def _handle_network_connection(self, reader, writer):
		data    = await reader.readline()
		message = data.decode()

		address = writer.get_extra_info('peername')
		logging.info(
			'Recieved "{}" from {}'.format(
				message.strip(),
				address,
			)
		)

		json_response = await self._handle_rpc(data)

		logging.info('Sending response back to {}:\n{}'.format(
			address,
			json_response.json,
		))
		writer.write(json_response.json.encode())
		await writer.drain()

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

