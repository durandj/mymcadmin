import asyncio
import asyncio.subprocess
import logging

class Manager(object):
	def __init__(self, server):
		self.server         = server
		self.proc           = None
		self.network_future = None

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
		create = self.server.start(
			stdin  = asyncio.subprocess.PIPE,
			stdout = asyncio.subprocess.PIPE,
			stderr = asyncio.subprocess.PIPE,
		)

		self.proc = await create

		await self.proc.wait()
		# self.network_future.cancel()

		return self.proc.returncode

