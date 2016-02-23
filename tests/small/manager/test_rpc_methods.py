"""
Tests for the JSON RPC interface handling
"""

import asyncio
import unittest

import asynctest
import nose

from ... import utils

from mymcadmin.errors import ServerDoesNotExistError
from mymcadmin.manager import Manager
from mymcadmin.rpc.errors import JsonRpcInvalidRequestError

# pylint: disable=too-many-public-methods
class TestRpcCommands(utils.EventLoopMixin, unittest.TestCase):
    """
    Tests for the JSON RPC commands
    """

    def setUp(self):
        super(TestRpcCommands, self).setUp()

        self.host            = 'example.com'
        self.port            = 8000
        self.root            = 'root'
        self.mock_event_loop = asynctest.Mock(spec = asyncio.BaseEventLoop)

        self.manager = Manager(
            self.host,
            self.port,
            self.root,
            event_loop = self.mock_event_loop,
        )

    @asynctest.patch('mymcadmin.server.Server')
    @asynctest.patch('os.path.exists')
    @utils.run_async
    async def test_server_start(self, exists, server):
        """
        Check that the start command starts a server
        """

        exists.return_value = True
        server.return_value = server

        server_id = 'testification'

        mock_start_server_proc = asynctest.CoroutineMock()

        self.manager.start_server_proc = mock_start_server_proc

        result = await self.manager.rpc_command_server_start(
            server_id = server_id,
        )

        self.assertEqual(
            server_id,
            result,
            'Did not return server ID',
        )

        mock_start_server_proc.assert_called_with(server)

    @nose.tools.raises(ServerDoesNotExistError)
    @utils.run_async
    async def test_server_start_bad_id(self):
        """
        Check that we return an error when we give an invalid ID
        """

        await self.manager.rpc_command_server_start(
            server_id = 'bad',
        )

    @nose.tools.raises(JsonRpcInvalidRequestError)
    @utils.run_async
    async def test_server_start_missing(self):
        """
        Chewck that we require the server_id parameter
        """

        await self.manager.rpc_command_server_start()

    @utils.run_async
    async def test_server_start_all(self):
        """
        Check that the startAll command starts all servers
        """

        server_ids = ['test0', 'test1', 'test2']

        mock_list_servers = asynctest.CoroutineMock()
        mock_list_servers.return_value = server_ids

        mock_server_start = asynctest.CoroutineMock()
        mock_server_start.side_effect = lambda s: s

        self.manager.rpc_command_list_servers = mock_list_servers
        self.manager.rpc_command_server_start = mock_server_start

        result = await self.manager.rpc_command_server_start_all()

        mock_server_start.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in server_ids
            ]
        )

        self.assertListEqual(
            server_ids,
            result.get('success'),
            'The list of successful servers did not match',
        )

        self.assertListEqual(
            [],
            result.get('failure'),
            'The list of failed servers did not match',
        )

    @utils.run_async
    async def test_server_start_all_started(self):
        """
        Check that we don't try and start servers that are already running
        """

        server_ids  = ['test0', 'test1', 'test2']
        running_ids = ['running0', 'running1']

        mock_list_servers = asynctest.CoroutineMock()
        mock_list_servers.return_value = server_ids + running_ids

        mock_server_start = asynctest.CoroutineMock()
        mock_server_start.side_effect = lambda s: s

        self.manager.rpc_command_list_servers = mock_list_servers
        self.manager.rpc_command_server_start = mock_server_start

        self.manager.instances = {
            server_id: asynctest.Mock()
            for server_id in running_ids
        }

        result = await self.manager.rpc_command_server_start_all()

        mock_server_start.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in server_ids
            ]
        )

        self.assertListEqual(
            server_ids,
            result.get('success'),
            'The list of successful servers did not match',
        )

        self.assertListEqual(
            [],
            result.get('failure'),
            'The list of failed servers did not match',
        )

    @utils.run_async
    async def test_server_start_all_errors(self):
        """
        Check that we keep trying to start servers even if one errors out
        """

        error_ids  = ['error0', 'error1']
        server_ids = ['success0', 'success1', 'success2']

        def _start_func(server_id):
            if server_id.startswith('success'):
                return server_id
            else:
                raise RuntimeError('Boom!')

        mock_list_servers = asynctest.CoroutineMock()
        mock_list_servers.return_value = error_ids + server_ids

        mock_server_start = asynctest.CoroutineMock()
        mock_server_start.side_effect = _start_func

        self.manager.rpc_command_list_servers = mock_list_servers
        self.manager.rpc_command_server_start = mock_server_start

        result = await self.manager.rpc_command_server_start_all()

        mock_server_start.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in server_ids
            ]
        )

        self.assertListEqual(
            server_ids,
            result.get('success'),
            'The list of successful servers did not match',
        )

        self.assertListEqual(
            error_ids,
            result.get('failure'),
            'The list of failed servers did not match',
        )

    @asynctest.patch('mymcadmin.server.Server')
    @asynctest.patch('os.path.exists')
    @utils.run_async
    async def test_server_stop(self, exists, server):
        """
        Check that the stop command stops a server
        """

        exists.return_value = True

        server.return_value = server

        server_id = 'testification'
        mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

        self.manager.instances = {
            server_id: mock_proc,
        }

        result = await self.manager.rpc_command_server_stop(
            server_id = server_id,
        )

        self.assertEqual(
            server_id,
            result,
            'Did not return the server ID',
        )

        mock_proc.communicate.assert_called_with('stop'.encode())

    @nose.tools.raises(ServerDoesNotExistError)
    @utils.run_async
    async def test_server_stop_bad_id(self):
        """
        Check that we return an error when we given an invalid ID
        """

        await self.manager.rpc_command_server_stop(
            server_id = 'bad',
        )

    @nose.tools.raises(JsonRpcInvalidRequestError)
    @asynctest.patch('os.path.exists')
    @utils.run_async
    async def test_server_stop_not_running(self, exists):
        """
        Check that we throw an error when the server isn't running
        """

        exists.return_value = True

        server_id = 'testification'

        await self.manager.rpc_command_server_stop(server_id)

    @utils.run_async
    async def test_server_stop_all(self):
        """
        Check that the stopAll command stops all servers
        """

        server_ids   = ['test0', 'test1', 'test2']
        server_procs = {
            server_id: asynctest.Mock(spec = asyncio.subprocess.Process)
            for server_id in server_ids
        }

        mock_list_servers = asynctest.CoroutineMock()
        mock_list_servers.return_value = server_ids

        mock_server_stop = asynctest.CoroutineMock()
        mock_server_stop.side_effect = lambda s: s

        self.manager.instances = server_procs

        self.manager.rpc_command_list_servers = mock_list_servers
        self.manager.rpc_command_server_stop  = mock_server_stop

        result = await self.manager.rpc_command_server_stop_all()

        mock_server_stop.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in self.manager.instances.keys()
            ]
        )

        self.assertListEqual(
            list(server_procs.keys()),
            result.get('success'),
            'The list of successful servers did not match',
        )

        self.assertListEqual(
            [],
            result.get('failure'),
            'The list of failed servers did not match',
        )

    @utils.run_async
    async def test_server_stop_all_errors(self):
        """
        Check that we keep going if one of the servers errors out
        """

        server_ids = ['success0', 'success1', 'success2']
        error_ids  = ['error0', 'error1']

        mock_procs = {
            server_id: asynctest.Mock(spec = asyncio.subprocess.Process)
            for server_id in (server_ids + error_ids)
        }

        def _stop_func(server_id):
            if server_id.startswith('success'):
                return server_id
            else:
                raise RuntimeError('Boom!')

        mock_server_stop = asynctest.CoroutineMock()
        mock_server_stop.side_effect = _stop_func

        self.manager.instances = mock_procs
        self.manager.rpc_command_server_stop = mock_server_stop

        result = await self.manager.rpc_command_server_stop_all()

        mock_server_stop.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in mock_procs.keys()
            ]
        )

        self.assertListEqual(
            [
                server_id
                for server_id in mock_procs.keys()
                if server_id.startswith('success')
            ],
            result.get('success'),
            'The list of successful servers did not match',
        )

        self.assertListEqual(
            [
                server_id
                for server_id in mock_procs.keys()
                if not server_id.startswith('success')
            ],
            result.get('failure'),
            'The list of failed servers did not match',
        )

    @utils.run_async
    async def test_shutdown_running_proc(self):
        """
        Check that the shutdown command stops any running server instances
        """

        instance_ids = ['test0', 'test1', 'test2', 'test3']
        instances    = {}
        for server_id in instance_ids:
            mock = asynctest.Mock(spec = asyncio.subprocess.Process)

            instances[server_id] = mock

        mock_server_stop = asynctest.CoroutineMock()
        self.manager.instances = instances
        self.manager.rpc_command_server_stop = mock_server_stop
        self.manager.rpc_command_server_stop.side_effect = instance_ids

        result = await self.manager.rpc_command_shutdown()

        self.assertEqual(
            instance_ids,
            result,
            'Return message did not match',
        )

        mock_server_stop.assert_has_calls(
            [
                unittest.mock.call(server_id = server_id)
                for server_id in instances.keys()
            ]
        )
# pylint: enable=too-many-public-methods

if __name__ == '__main__':
    unittest.main()

