"""
JSON RPC client
"""

import asyncio
import json
import logging

from . import errors, request
from .. import utils

class RpcClient(object):
    """
    JSON RPC client
    """

    def __init__(self, host, port, event_loop = None):
        if event_loop is None:
            event_loop = asyncio.get_event_loop()

        self.event_loop = event_loop
        self.host       = host
        self.port       = port
        self.reader     = None
        self.writer     = None

    def start(self):
        """
        Start the JSON RPC client
        """

        utils.setup_logging()

        logging.info('Setting up network connection')
        self.event_loop.run_until_complete(self._connect())

    def stop(self):
        """
        Stop the JSON RPC client
        """

        self.event_loop.close()

    def list_servers(self):
        """
        Get the list of available servers
        """

        return self.execute_rpc_method('list_servers')

    def shutdown(self):
        """
        Ask the management process to stop
        """

        return self.execute_rpc_method('shutdown')

    def server_create(self, server_id, version = None):
        """
        Ask the management process to create a Minecraft server
        """

        params = {
            'server_id': server_id,
        }

        if version is not None:
            params['version'] = version

        return self.execute_rpc_method(
            'server_create',
            params,
        )

    def server_start(self, server_id):
        """
        Ask the management process to start a Minecraft server
        """

        return self.execute_rpc_method('server_start', {'server_id': server_id})

    def server_start_all(self):
        """
        Ask the management process to start all the Minecraft servers
        """

        return self.execute_rpc_method('server_start_all')

    def server_stop(self, server_id):
        """
        Ask the management process to stop a Minecraft server
        """

        return self.execute_rpc_method('server_stop', {'server_id': server_id})

    def server_stop_all(self):
        """
        Ask the management process to stop all the Minecraft servers
        """

        return self.execute_rpc_method('server_stop_all')

    def server_restart(self, server_id):
        """
        Ask the management process to restart a Minecraft server
        """

        return self.execute_rpc_method('server_restart', {'server_id': server_id})

    def server_restart_all(self):
        """
        Ask the management process to restart all the Minecraft servers
        """

        return self.execute_rpc_method('server_restart_all')

    def execute_rpc_method(self, method, params = None):
        """
        Execute a JSON RPC command on the management server
        """

        return self.event_loop.run_until_complete(
            self._send(method, params)
        )

    def __enter__(self):
        self.start()

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()

    async def _connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.host,
            self.port,
            loop = self.event_loop,
        )

    async def _send(self, method, params, request_id = 1):
        data = request.JsonRpcRequest(
            method     = method,
            params     = params,
            request_id = request_id,
        ).json

        logging.info('Sending "%s" to server', data)
        self.writer.write(data.encode())
        self.writer.write_eof()
        await self.writer.drain()

        logging.info('Waiting for server response')
        response = await self.reader.readline()
        response = response.decode()
        logging.info('Received "%s" from the server', response)
        response = json.loads(response)

        if 'error' in response:
            raise errors.JsonRpcError(
                'RPC error: {}',
                response['error']['message'],
            )

        return response['result']

