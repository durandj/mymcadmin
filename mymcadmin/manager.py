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
                'list_servers':       self.rpc_command_list_servers,
                'server_restart':     self.rpc_command_server_restart,
                'server_restart_all': self.rpc_command_server_restart_all,
                'server_start':       self.rpc_command_server_start,
                'server_start_all':   self.rpc_command_server_start_all,
                'server_stop':        self.rpc_command_server_stop,
                'server_stop_all':    self.rpc_command_server_stop_all,
                'shutdown':           self.rpc_command_shutdown,
            }
        )

    async def rpc_command_list_servers(self):
        """
        Handle RPC command: listServers
        """

        files = [
            f
            for f in os.listdir(self.root)
            if os.path.isdir(os.path.join(self.root, f))
        ]

        return files

    @rpc.required_param('server_id')
    async def rpc_command_server_restart(self, server_id):
        """
        Handle RPC command: serverRestart
        """

        logging.info('Sending restart command to server %s', server_id)

        await self.rpc_command_server_stop(server_id = server_id)
        await self.rpc_command_server_start(server_id = server_id)

        return server_id

    async def rpc_command_server_restart_all(self):
        """
        Handle RPC command: serverRestartAll
        """

        logging.info('Restarting all servers...')

        restarted_servers = []
        for server_id in self.instances.keys():
            # pylint: disable=broad-except
            try:
                result = await self.rpc_command_server_restart(server_id)

                restarted_servers.append(result)
            except Exception as ex:
                logging.exception(
                    'There was an error when restarting server %s: %s',
                    server_id,
                    str(ex),
                )
            # pylint: enable=broad-except

        return restarted_servers

    @rpc.required_param('server_id')
    async def rpc_command_server_start(self, server_id):
        """
        Handle RPC command: serverStart
        """

        srv = self._get_server_by_id(server_id)

        logging.info('Starting Minecraft server %s', server_id)

        self.event_loop.create_task(self.start_server_proc(srv))

        return server_id

    async def rpc_command_server_start_all(self):
        """
        Handle RPC command: serverStartAll
        """

        server_ids  = await self.rpc_command_list_servers()
        running_ids = self.instances.keys()
        server_ids  = [
            server_id
            for server_id in server_ids
            if server_id not in running_ids
        ]

        started_servers = []
        for server_id in server_ids:
            # pylint: disable=broad-except
            try:
                server_id = await self.rpc_command_server_start(server_id)

                started_servers.append(server_id)
            except Exception as ex:
                logging.exception(
                    'There was an error when starting server %s: %s',
                    server_id,
                    str(ex),
                )
            # pylint: enable=broad-except

        return started_servers

    @rpc.required_param('server_id')
    async def rpc_command_server_stop(self, server_id):
        """
        Handle RPC command: serverStop
        """

        proc = self._get_proc_by_id(server_id)
        if proc is None:
            raise rpc_errors.JsonRpcInvalidRequestError(
                'Server {} was not running',
                server_id,
            )

        logging.info('Sending stop command to server %s', server_id)

        await self._send_to_server(proc, 'stop')

        return server_id

    async def rpc_command_server_stop_all(self):
        """
        Handle RPC command: serverStopAll
        """

        server_ids = self.instances.keys()

        stopped_servers = []
        for server_id in server_ids:
            # pylint: disable=broad-except
            try:
                result = await self.rpc_command_server_stop(server_id)

                stopped_servers.append(result)
            except Exception as ex:
                logging.exception(
                    'There was an error stopping server %s: %s',
                    server_id,
                    str(ex),
                )
            # pylint: enable=broad-except

        return stopped_servers

    async def rpc_command_shutdown(self):
        """
        Handle RPC command: terminate
        """

        logging.info('Sending terminate command to management server')

        stopped_instances = []
        if self.instances:
            for server_id in self.instances.keys():
                # pylint: disable=broad-except
                try:
                    stopped_instances.append(
                        await self.rpc_command_server_stop(server_id)
                    )
                except Exception as ex:
                    logging.exception(str(ex))
                # pylint: enable=broad-except

        self.event_loop.stop()

        return stopped_instances

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

        self.instances[srv.server_id] = proc

        await proc.wait()

        del self.instances[srv.server_id]

    def _get_all_server_paths(self):
        server_paths = [
            os.path.join(self.root, server_path)
            for server_path in os.listdir(self.root)
            if os.path.isdir(os.path.join(self.root, server_path))
        ]

        return server_paths

    def _get_server_by_id(self, server_id):
        server_path = os.path.join(self.root, server_id)
        if not os.path.exists(server_path):
            raise errors.ServerDoesNotExistError(server_id)

        return server.Server(server_path)

    def _get_proc_by_id(self, server_id):
        server_path = os.path.join(self.root, server_id)
        if not os.path.exists(server_path):
            raise errors.ServerDoesNotExistError(server_id)

        return self.instances.get(server_id, None)

    @staticmethod
    async def _send_to_server(proc, message):
        return proc.communicate(message.encode())

