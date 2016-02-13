"""
Management process for Minecraft servers.
"""

import asyncio
import asyncio.subprocess
import logging
import os.path

from . import errors, rpc, server
from .rpc import errors as rpc_errors

class Manager(object):
    """
    Minecraft server management system.
    """

    def __init__(self, host, port, root, event_loop = None):
        logging.info('Setting up event loop')

        if event_loop is None:
            event_loop = asyncio.get_event_loop()

        self.host           = host
        self.port           = port
        self.root           = root
        self.event_loop     = event_loop
        self.instances      = {}
        self.network_task   = None
        self.rpc_dispatcher = rpc.Dispatcher()

        self._setup_rpc_handlers()

    def run(self):
        """
        Start and run the management process
        """

        logging.info('Setting up network connection')
        self.network_task = self.event_loop.create_task(
            asyncio.start_server(
                self.handle_network_connection,
                self.host,
                self.port,
                loop = self.event_loop,
            )
        )

        # TODO(durandj): check for servers to auto start

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
                'shutdown':      self.rpc_command_shutdown,
                'serverStart':   self.rpc_command_server_start,
                'serverStop':    self.rpc_command_server_stop,
                'serverRestart': self.rpc_command_server_restart,
            }
        )

    async def rpc_command_shutdown(self):
        """
        Handle RPC command: terminate
        """

        logging.info('Sending terminate command to management server')

        stopped_instances = []
        if self.instances:
            for server_id in self.instances.keys():
                # TODO(durandj): can this method throw an exception that'll get in the way?
                stopped_instances.append(
                    await self.rpc_command_server_stop(server_id)
                )

        self.event_loop.stop()

        return stopped_instances

    # TODO(durandj): check for required parameters
    async def rpc_command_server_start(self, server_id):
        """
        Handle RPC command: serverStart
        """

        srv = self._get_server_by_name(server_id)

        logging.info('Starting Minecraft server %s', server_id)

        self.event_loop.create_task(self.start_server_proc(srv))

        return server_id

    async def rpc_command_server_stop(self, server_id):
        """
        Handle RPC command: serverStop
        """

        proc = self._get_proc_by_name(server_id)
        if proc is None:
            raise rpc_errors.JsonRpcInvalidRequestError(
                'Server %s was not running',
                server_id,
            )

        logging.info('Sending stop command to server %s', server_id)

        await self._send_to_server(proc, 'stop')

        return server_id

    async def rpc_command_server_restart(self, server_id):
        """
        Handle RPC command: serverRestart
        """

        logging.info('Sending restart command to server %s', server_id)

        await self.rpc_command_server_stop(server_id)
        await self.rpc_command_server_start(server_id)

        return server_id

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

    async def start_server_proc(self, srv):
        """
        Handle process management
        """

        proc = await srv.start()

        self.instances[srv.name] = proc

        await proc.wait()

    def _get_server_by_name(self, name):
        server_path = os.path.join(self.root, name)
        if not os.path.exists(server_path):
            raise errors.ServerDoesNotExistError(name)

        return server.Server(server_path)

    def _get_proc_by_name(self, name):
        server_path = os.path.join(self.root, name)
        if not os.path.exists(server_path):
            raise errors.ServerDoesNotExistError(name)

        return self.instances.get(name, None)

    @staticmethod
    async def _send_to_server(proc, message):
        return proc.communicate(message.encode())

