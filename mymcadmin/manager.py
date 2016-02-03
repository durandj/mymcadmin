import asyncio
import asyncio.subprocess
import logging

class Manager(object):
	def __init__(self, server):
		self.server = server
		self.proc   = None

	@asyncio.coroutine
	def handle_network_connection(self, reader, writer):
		data    = yield from reader.readline()
		message = data.decode()

		address = writer.get_extra_info('peername')
		logging.info(
			'Recieved "{}" from {}'.format(
				message,
				address,
			)
		)

		yield from self.proc.communicate(data)
		# writer.write(data)
		# yield from writer.drain()

		writer.close()

	@asyncio.coroutine
	def handle_proc(self):
		create = self.server.start(
			stdin  = asyncio.subprocess.PIPE,
			stdout = asyncio.subprocess.PIPE,
			stderr = asyncio.subprocess.PIPE,
		)

		self.proc = yield from create

		yield from self.proc.wait()

		return self.proc.returncode

