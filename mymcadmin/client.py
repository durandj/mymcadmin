import asyncio
import logging

from . import utils

class Client(object):
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

	def send_message(self, message):
		self.event_loop.run_until_complete(self._send(message))

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

	async def _send(self, message):
		logging.info('Sending "{}" to server'.format(message))

		self.writer.write(message.encode())

