import asyncio
import json
import logging

from . import rpc, utils

class Client(object):
	JSONRPC_VERSION = '2.0'

	def __init__(self, host, port):
		self.event_loop = asyncio.get_event_loop()
		self.host       = host
		self.port       = port
		self.reader     = None
		self.writer     = None

	def run(self):
		utils.setup_logging()

		logging.info('Setting up network connection')
		self.event_loop.run_until_complete(self._setup())

	def stop(self):
		self.event_loop.close()

	def terminate(self):
		self.send_rpc_command('terminate')

	def server_start(self):
		self.send_rpc_command('serverStart')

	def server_stop(self):
		self.send_rpc_command('serverStop')

	def server_restart(self):
		self.send_rpc_command('serverRestart')

	def send_rpc_command(self, command, params = {}):
		self.event_loop.run_until_complete(self._send(command, params))

	def __enter__(self):
		self.run()

		return self

	def __exit__(self, exception_type, exception_value, traceback):
		self.stop()

	async def _setup(self):
		self.reader, self.writer = await asyncio.open_connection(
			self.host,
			self.port,
			loop = self.event_loop,
		)

	async def _send(self, method, params, request_id = 1):
		data = json.dumps(
			{
				'jsonrpc': Client.JSONRPC_VERSION,
				'id':      request_id,
				'method':  method,
				'params':  params,
			}
		) + '\n'

		logging.info('Sending "{}" to server'.format(data))
		self.writer.write(data.encode())

		logging.info('Waiting for server response')
		response = await self.reader.read()
		response = response.decode()
		logging.info('Received "{}" from the server'.format(response))
		response = json.loads(response)

		if 'error' in response:
			raise rpc.JsonRpcError(
				'RPC error: {}',
				response['error']['message'],
			)

