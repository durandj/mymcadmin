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
			logging.info('Management process terminated')

	def _setup_rpc_handlers(self):
		logging.info('Setting up JSON RPC handlers')

		self.rpc_dispatcher.add_dict(
			{
				'terminate':     self._rpc_command_terminate,
				'serverStart':   self._rpc_command_server_start,
				'serverStop':    self._rpc_command_server_stop,
				'serverRestart': self._rpc_command_server_restart,
			}
		)

	async def _rpc_command_terminate(self, **kwargs):
		logging.info('Sending terminate command to management server')

		if self.proc.returncode is None:
			await self._rpc_command_server_stop()
			await self.proc.wait()
		self.event_loop.stop()

		return 'terminating manager'

	async def _rpc_command_server_start(self, **kwargs):
		logging.info('Starting Minecraft server')

		self.event_loop.create_task(self._handle_proc())

		return 'starting server'

	async def _rpc_command_server_stop(self, **kwargs):
		logging.info('Sending stop command to server')

		await self.proc.communicate('stop'.encode())

		return 'stopping server'

	async def _rpc_command_server_restart(self, **kwargs):
		logging.info('Sending restart command to server')

		await self._rpc_command_server_stop()
		await self._rpc_command_server_start()

		return 'restarting server'

	async def _handle_network_connection(self, reader, writer):
		data    = await reader.readline()
		message = data.decode()

		address = writer.get_extra_info('peername')
		logging.info(
			'Recieved "{}" from client {}'.format(
				message.strip(),
				address,
			)
		)

		json_response = await rpc.JsonRpcResponseManager.handle(
			data,
			self.rpc_dispatcher,
		)

		logging.info('Sending response back to {}:\n{}'.format(
			address,
			json_response.json,
		))
		writer.write(json_response.json.encode())
		await writer.drain()

		writer.close()

	async def _handle_proc(self):
		create = self.server.start()

		self.proc = await create

		await self.proc.wait()

