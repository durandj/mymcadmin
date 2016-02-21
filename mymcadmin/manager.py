"""
Management process for Minecraft servers.
"""

import asyncio
import asyncio.subprocess
import logging
import os.path

from . import errors, forge as forge_utils, rpc, server
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

        logging.info('Auto starting servers')
        for server_path in self._get_all_server_paths():
            server_instance = server.Server(server_path)
            autostart = server_instance.settings.get('autostart', False)

            if not autostart:
                continue

            logging.info('Starting server %s', server_instance.server_id)
            self.event_loop.create_task(
                self.start_server_proc(server_instance)
            )

        logging.info('Management process running')
        try:
            self.event_loop.run_forever()
        finally:
            logging.info('Waiting for remaining processes to finish')
            remaining_tasks = asyncio.Task.all_tasks()
            self.event_loop.run_until_complete(asyncio.gather(*remaining_tasks))
            logging.info('Shutting down management process')
            self.event_loop.close()
            logging.info('Management process terminated')

    def _setup_rpc_handlers(self):
        logging.info('Setting up JSON RPC handlers')

        self.rpc_dispatcher.add_dict(
            {
                'list_servers':       self.rpc_command_list_servers,
                'server_create':      self.rpc_command_server_create,
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

        return [
            os.path.basename(server_path)
            for server_path in self._get_all_server_paths()
        ]

    @rpc.required_param('server_id')
    async def rpc_command_server_create(self, server_id, version = None, forge = None):
        """
        Handle RPC command: server_create
        """

        logging.info('Preparing to create server %s', server_id)

        server_path = os.path.join(self.root, server_id)

        if os.path.exists(server_path):
            raise errors.ServerExistsError(server_id)

        logging.info('Creating directory for instance %s', server_id)
        os.mkdir(server_path)

        logging.info('Downloading server jar')
        jar = server.Server.download_server_jar(version, path = server_path)

        logging.info('Generating a default settings file')
        server.Server.generate_default_settings(
            path = server_path,
            jar  = jar,
        )

        logging.info('Starting server for the first time')
        srv  = server.Server(server_path)
        proc = await srv.start()

        await proc.wait()
        logging.info('Server stopped')

        logging.info('Marking EULA as accepted')
        server.Server.agree_to_eula(path = server_path)

        if forge is not None:
            logging.info('Setting up Forge')
            if forge is True:
                logging.info(
                    'Downloading latest Forge for Minecraft %s',
                    version,
                )

                jar_path = forge_utils.get_forge_for_mc_version(
                    version,
                    path = server_path,
                )
            elif isinstance(forge, str):
                logging.info(
                    'Downloading Forge %s for Minecraft',
                    forge,
                )

                jar_path = forge_utils.get_forge_version(
                    version,
                    forge,
                    path = server_path,
                )

            logging.info('Configuring server to use Forge')
            srv.settings['jar'] = os.path.basename(jar_path)
            srv.save_settings()

        return server_id

    @rpc.required_param('server_id')
    async def rpc_command_server_restart(self, server_id):
        """
        Handle RPC command: server_restart
        """

        logging.info('Sending restart command to server %s', server_id)

        await self.rpc_command_server_stop(server_id = server_id)
        await self.rpc_command_server_start(server_id = server_id)

        return server_id

    async def rpc_command_server_restart_all(self):
        """
        Handle RPC command: server_restart_all
        """

        logging.info('Restarting all servers...')

        success = []
        failure = []
        for server_id in self.instances.keys():
            # pylint: disable=broad-except
            try:
                result = await self.rpc_command_server_restart(server_id)

                success.append(result)
            except Exception as ex:
                logging.exception(
                    'There was an error when restarting server %s: %s',
                    server_id,
                    str(ex),
                )
                failure.append(server_id)
            # pylint: enable=broad-except

        return {'success': success, 'failure': failure}

    @rpc.required_param('server_id')
    async def rpc_command_server_start(self, server_id):
        """
        Handle RPC command: server_start
        """

        srv = self._get_server_by_id(server_id)

        logging.info('Starting Minecraft server %s', server_id)

        self.event_loop.create_task(self.start_server_proc(srv))

        return server_id

    async def rpc_command_server_start_all(self):
        """
        Handle RPC command: server_start_all
        """

        server_ids  = await self.rpc_command_list_servers()
        running_ids = self.instances.keys()
        server_ids  = [
            server_id
            for server_id in server_ids
            if server_id not in running_ids
        ]

        success = []
        failure = []
        for server_id in server_ids:
            # pylint: disable=broad-except
            try:
                server_id = await self.rpc_command_server_start(server_id)

                success.append(server_id)
            except Exception as ex:
                logging.exception(
                    'There was an error when starting server %s: %s',
                    server_id,
                    str(ex),
                )
                failure.append(server_id)
            # pylint: enable=broad-except

        return {'success': success, 'failure': failure}

    @rpc.required_param('server_id')
    async def rpc_command_server_stop(self, server_id):
        """
        Handle RPC command: server_stop
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
        Handle RPC command: server_stop_all
        """

        server_ids = self.instances.keys()

        success = []
        failure = []
        for server_id in server_ids:
            # pylint: disable=broad-except
            try:
                result = await self.rpc_command_server_stop(server_id)

                success.append(result)
            except Exception as ex:
                logging.exception(
                    'There was an error stopping server %s: %s',
                    server_id,
                    str(ex),
                )
                failure.append(server_id)
            # pylint: enable=broad-except

        return {'success': success, 'failure': failure}

    async def rpc_command_shutdown(self):
        """
        Handle RPC command: shutdown
        """

        logging.info('Shutting down...')

        stopped_instances = []
        if self.instances:
            for server_id in list(self.instances.keys()):
                # pylint: disable=broad-except
                try:
                    stopped_instances.append(
                        await self.rpc_command_server_stop(server_id = server_id)
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

        data    = await reader.read()
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

        response_data = json_response.json

        logging.info(
            'Sending response back to %s:\n%s',
            address,
            response_data,
        )
        writer.write(response_data.encode())
        writer.write_eof()
        await writer.drain()

        writer.close()

    async def start_server_proc(self, srv):
        """
        Handle process management
        """

        proc = await srv.start()

        self.instances[srv.server_id] = proc

        await proc.wait()

        if proc.returncode != 0:
            logging.error('Server %s ran into an error', srv.server_id)

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
        return await proc.communicate(message.encode())

