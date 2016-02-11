"""
Management process for Minecraft servers.
"""

import asyncio
import asyncio.subprocess
import logging

from . import rpc

class Manager(object):
    """
    Minecraft server management system.
    """

    def __init__(self, server, event_loop = None):
        logging.info('Setting up event loop')

        if event_loop is None:
            event_loop = asyncio.get_event_loop()

        self.server         = server
        self.event_loop     = event_loop
        self.proc           = None
        self.network_task   = None
        self.rpc_dispatcher = rpc.Dispatcher()

        self._setup_rpc_handlers()

    def run(self):
        """
        Start and run the management process
        """

        _, host, port = self.server.socket_settings

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
                'terminate':     self.rpc_command_terminate,
                'serverStart':   self.rpc_command_server_start,
                'serverStop':    self.rpc_command_server_stop,
                'serverRestart': self.rpc_command_server_restart,
            }
        )

    async def rpc_command_terminate(self):
        """
        Handle RPC command: terminate
        """

        logging.info('Sending terminate command to management server')

        if self.proc.returncode is None:
            await self.rpc_command_server_stop()
            await self.proc.wait()
        self.event_loop.stop()

        return 'terminating manager'

    async def rpc_command_server_start(self):
        """
        Handle RPC command: serverStart
        """

        logging.info('Starting Minecraft server')

        self.event_loop.create_task(self.handle_proc())

        return 'starting server'

    async def rpc_command_server_stop(self):
        """
        Handle RPC command: serverStop
        """

        logging.info('Sending stop command to server')

        await self.proc.communicate('stop'.encode())

        return 'stopping server'

    async def rpc_command_server_restart(self):
        """
        Handle RPC command: serverRestart
        """

        logging.info('Sending restart command to server')

        await self.rpc_command_server_stop()
        await self.rpc_command_server_start()

        return 'restarting server'

    async def handle_network_connection(self, reader, writer):
        """
        Handle network connections
        """

        data    = await reader.readline()
        message = data.decode()

        address = writer.get_extra_info('peername')
        logging.info(
            'Recieved "%s" from client %s',
            message.strip(),
            address,
        )

        json_response = await rpc.JsonRpcResponseManager.handle(
            data,
            self.rpc_dispatcher,
        )

        logging.info(
            'Sending response back to %s:\n%s',
            address,
            json_response.json,
        )
        writer.write(json_response.json.encode())
        await writer.drain()

        writer.close()

    async def handle_proc(self):
        """
        Handle process management
        """

        self.proc = await self.server.start()

        await self.proc.wait()

