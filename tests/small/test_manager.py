"""
Tests for the mymcadmin.manager.Manager class
"""

import asyncio
import asyncio.subprocess
import json
import os.path
import unittest

import asynctest
import nose

from .. import utils

from mymcadmin.errors import ServerDoesNotExistError, ServerExistsError
from mymcadmin.manager import Manager
from mymcadmin.rpc.errors import JsonRpcInvalidRequestError
from mymcadmin.server import Server

class TestManager(unittest.TestCase):
    """
    Tests for the mymcadmin.manager.Manager class
    """

    def setUp(self):
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        self.host = 'example.com'
        self.port = 8000
        self.root = 'root'

    def tearDown(self):
        self.event_loop.close()

    @asynctest.patch('asyncio.gather')
    @asynctest.patch('asyncio.Task.all_tasks')
    @asynctest.patch('mymcadmin.server.Server')
    @asynctest.patch('os.path.isdir')
    @asynctest.patch('os.listdir')
    @asynctest.patch('mymcadmin.manager.Manager.handle_network_connection')
    @asynctest.patch('asyncio.start_server')
    def test_run(self, start_server, handle_network, listdir, isdir, server, all_tasks, gather):
        """
        Check that the run function starts and stops the event loop
        """

        server_ids = [
            'server0',
            'autoserver1',
            'autoserver2',
            'server3',
        ]

        mock_event_loop = asynctest.Mock(asyncio.BaseEventLoop)

        listdir.return_value = server_ids

        isdir.return_value = True

        mock_servers = [
            unittest.mock.Mock(
                spec      = Server,
                server_id = server_id,
                settings  = {
                    'autostart': server_id.startswith('auto'),
                },
            )
            for server_id in server_ids
        ]

        server.side_effect = mock_servers

        all_tasks.return_value = server_ids

        gather.return_value = gather

        mock_start_server_proc = asynctest.CoroutineMock()
        mock_start_server_proc.return_value = mock_start_server_proc

        manager = Manager(
            self.host,
            self.port,
            self.root,
            event_loop = mock_event_loop,
        )
        manager.start_server_proc = mock_start_server_proc

        manager.run()

        asyncio.set_event_loop(self.event_loop)

        start_server.assert_called_with(
            handle_network,
            self.host,
            self.port,
            loop = mock_event_loop,
        )

        manager.start_server_proc.assert_has_calls(
            [
                unittest.mock.call(mock_server)
                for mock_server in mock_servers
                if mock_server.server_id.startswith('auto')
            ]
        )

        mock_event_loop.run_forever.assert_called_with()

        all_tasks.assert_called_with()
        gather.assert_called_with(*server_ids)
        mock_event_loop.run_until_complete.assert_called_with(gather)

        mock_event_loop.close.assert_called_with()

    @asynctest.patch('mymcadmin.rpc.JsonRpcResponseManager')
    @utils.run_async
    async def test_handle_network_connection(self, response_manager):
        """
        Check that the network handling handles all of the commands properly
        """

        mock_response = unittest.mock.Mock()
        mock_response.json = json.dumps(
            {
                'jsonrpc': '2.0',
                'id':      1,
                'result':  {'mission': 'complete'},
            }
        )

        response_manager.handle = asynctest.CoroutineMock()
        response_manager.handle.return_value = mock_response

        mock_event_loop = asynctest.Mock(spec = asyncio.BaseEventLoop)

        mock_reader = asynctest.Mock(spec = asyncio.StreamReader)

        mock_writer = asynctest.Mock(spec = asyncio.StreamWriter)
        mock_writer.get_extra_info.return_value = '127.0.0.1'

        response_future = asyncio.Future()
        mock_writer.write.side_effect = response_future.set_result

        req = json.dumps(
            {
                'jsonrpc': '2.0',
                'method':  'test',
                'params':  {'im': 'a test'},
                'id':      1,
            }
        ).encode()
        mock_reader.read.return_value = req

        manager = Manager(
            self.host,
            self.port,
            self.root,
            event_loop = mock_event_loop,
        )

        await manager.handle_network_connection(mock_reader, mock_writer)

        response_manager.handle.assert_called_with(req, manager.rpc_dispatcher)

        self.assertTrue(
            response_future.done(),
            'Response was never sent',
        )

        resp = json.loads(response_future.result().decode())
        self.assertDictEqual(
            {
                'jsonrpc': '2.0',
                'id':      1,
                'result':  {'mission': 'complete'},
            },
            resp,
        )

        mock_writer.write_eof.assert_called_with()
        mock_writer.drain.assert_called_with()

    @utils.run_async
    async def test_start_server_proc(self):
        """
        Check that the proc is started and waited for properly
        """

        mock_event_loop = asynctest.Mock(spec = asyncio.BaseEventLoop)
        mock_event_loop.run_until_complete.side_effect = \
                self.event_loop.run_until_complete

        mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

        mock_proc_func = asynctest.CoroutineMock()
        mock_proc_func.return_value = mock_proc

        mock_server = asynctest.Mock(spec = Server)
        mock_server.server_id = 'test'
        mock_server.start     = asynctest.CoroutineMock()
        mock_server.start.return_value = mock_proc_func()

        mock_instances = unittest.mock.MagicMock()

        manager = Manager(
            self.host,
            self.port,
            self.root,
            event_loop = mock_event_loop,
        )
        manager.instances = mock_instances

        await manager.start_server_proc(mock_server)

        mock_server.start.assert_called_with()
        mock_proc.wait.assert_called_with()

        mock_instances.__setitem__.assert_called_with('test', mock_proc)
        mock_instances.__delitem__.assert_called_with('test')

    @unittest.mock.patch('logging.error')
    @utils.run_async
    async def test_start_server_proc_crash(self, mock_error):
        """
        Tests that we log when the server instance crashes
        """

        mock_event_loop = asynctest.Mock(spec = asyncio.BaseEventLoop)

        mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

        mock_proc_func = asynctest.CoroutineMock()
        mock_proc_func.return_value = mock_proc
        mock_proc_func.returncode   = 1

        mock_server = asynctest.Mock(spec = Server)
        mock_server.server_id = 'test'
        mock_server.start.return_value = mock_proc_func()

        manager = Manager(
            self.host,
            self.port,
            self.root,
            event_loop = mock_event_loop,
        )

        await manager.start_server_proc(mock_server)

        mock_error.assert_called_with(
            'Server %s ran into an error',
            'test',
        )

    @utils.run_async
    async def test_rpc_method_handlers(self):
        """
        Tests that the correct handlers are assigned for RPC methods
        """

        manager = Manager(
            self.host,
            self.port,
            self.root,
        )

        def _test_method(name, method):
            self.assertEqual(
                method,
                manager.rpc_dispatcher[name],
                'Method handler was not correct',
            )

        _test_method('list_servers',       manager.rpc_command_list_servers)
        _test_method('server_create',      manager.rpc_command_server_create)
        _test_method('server_restart',     manager.rpc_command_server_restart)
        _test_method('server_restart_all', manager.rpc_command_server_restart_all)
        _test_method('server_start',       manager.rpc_command_server_start)
        _test_method('server_start_all',   manager.rpc_command_server_start_all)
        _test_method('server_stop',        manager.rpc_command_server_stop)
        _test_method('server_stop_all',    manager.rpc_command_server_stop_all)
        _test_method('shutdown',           manager.rpc_command_shutdown)

# pylint: disable=too-many-public-methods
class TestRpcCommands(unittest.TestCase):
    """
    Tests for the JSON RPC commands
    """

    def setUp(self):
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

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

    def tearDown(self):
        self.event_loop.close()

    @unittest.mock.patch('os.path.isdir')
    @unittest.mock.patch('os.listdir')
    @utils.run_async
    async def test_list_servers(self, listdir, isdir):
        """
        Check that the listServers command lists servers
        """

        listdir.return_value = [
            'test0',
            'test1',
            'test2',
            'conf',
        ]

        isdir.side_effect = lambda p: p.startswith(os.path.join(self.root, 'test'))

        result = await self.manager.rpc_command_list_servers()

        self.assertListEqual(
            ['test0', 'test1', 'test2'],
            result,
            'The server list was not correct',
        )

    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.mkdir')
    @unittest.mock.patch('os.path.exists')
    @utils.run_async
    async def test_server_create(self, exists, mkdir, server):
        """
        Tests that the server_create method creates a new server
        """

        version = 'stable-release'
        jar     = 'minecraft-stable-release.jar'

        server_id   = 'testification'
        server_path = os.path.join(self.root, server_id)

        exists.return_value = False

        server.download_server_jar.return_value = jar

        mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

        server.return_value = server
        server.start = asynctest.CoroutineMock()
        server.start.return_value = mock_proc

        result = await self.manager.rpc_command_server_create(
            server_id = server_id,
            version   = version,
        )

        self.assertEqual(
            server_id,
            result,
            'RPC response did not match',
        )

        mkdir.assert_called_with(server_path)

        server.download_server_jar.assert_called_with(
            version,
            path = server_path,
        )

        server.generate_default_settings.assert_called_with(
            path = server_path,
            jar  = jar,
        )

        server.assert_called_with(server_path)

        mock_proc.wait.assert_called_with()

        server.agree_to_eula.assert_called_with(
            path = server_path,
        )

    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.mkdir')
    @unittest.mock.patch('os.path.exists')
    @utils.run_async
    async def test_server_create_latest(self, exists, mkdir, server):
        """
        Tests that the server_create method gets the latest version by default
        """

        jar = 'minecraft-stable-release.jar'

        server_id   = 'testification'
        server_path = os.path.join(self.root, server_id)

        exists.return_value = False

        server.download_server_jar.return_value = jar

        mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

        server.return_value = server
        server.start = asynctest.CoroutineMock()
        server.start.return_value = mock_proc

        result = await self.manager.rpc_command_server_create(
            server_id = server_id,
        )

        self.assertEqual(
            server_id,
            result,
            'RPC response did not match',
        )

        mkdir.assert_called_with(server_path)

        server.download_server_jar.assert_called_with(
            None,
            path = server_path,
        )

        server.generate_default_settings.assert_called_with(
            path = server_path,
            jar  = jar,
        )

        server.assert_called_with(server_path)

        mock_proc.wait.assert_called_with()

        server.agree_to_eula.assert_called_with(
            path = server_path,
        )

    @nose.tools.raises(ServerExistsError)
    @unittest.mock.patch('os.path.exists')
    @utils.run_async
    async def test_server_create_exists(self, exists):
        """
        Tests that the server_create method checks if the server_id is in use
        """

        server_id = 'testification'

        exists.side_effect = lambda p: p.endswith(server_id)

        await self.manager.rpc_command_server_create(server_id = server_id)

    @utils.run_async
    async def test_server_restart(self):
        """
        Check that the restart command restarts a server
        """

        server_id = 'testification'

        mock_rpc_server_stop  = asynctest.CoroutineMock()
        mock_rpc_server_start = asynctest.CoroutineMock()

        self.manager.rpc_command_server_stop  = mock_rpc_server_stop
        self.manager.rpc_command_server_start = mock_rpc_server_start

        result = await self.manager.rpc_command_server_restart(
            server_id = server_id,
        )

        self.assertEqual(
            server_id,
            result,
            'RPC method did not return the right value',
        )

        mock_rpc_server_stop.assert_called_with(server_id = server_id)
        mock_rpc_server_start.assert_called_with(server_id = server_id)

    @nose.tools.raises(ServerDoesNotExistError)
    @utils.run_async
    async def test_server_restart_bad_id(self):
        """
        Check that we return an error when we give an invalid ID
        """

        await self.manager.rpc_command_server_restart(
            server_id = 'bad',
        )

    @nose.tools.raises(JsonRpcInvalidRequestError)
    @utils.run_async
    async def test_server_restart_missing(self):
        """
        Check that we require the server_id parameter
        """

        await self.manager.rpc_command_server_restart()

    @nose.tools.raises(RuntimeError)
    @utils.run_async
    async def test_server_restart_fail(self):
        """
        Check that if one of the restart steps fails we still handle it
        """

        mock_rpc_server_stop  = asynctest.CoroutineMock()
        mock_rpc_server_start = asynctest.CoroutineMock()

        mock_rpc_server_stop.side_effect = RuntimeError('Server not running')

        self.manager.rpc_command_server_stop  = mock_rpc_server_stop
        self.manager.rpc_command_server_start = mock_rpc_server_start

        await self.manager.rpc_command_server_restart(
            server_id = 'testification',
        )

    @utils.run_async
    async def test_server_restart_all(self):
        """
        Check that the restartAll command restarts all servers
        """

        server_ids = ['test0', 'test1', 'test2']

        mock_rpc_command_server_restart = asynctest.CoroutineMock()
        mock_rpc_command_server_restart.side_effect = server_ids

        self.manager.instances = {
            server_id: asynctest.Mock()
            for server_id in server_ids
        }

        self.manager.rpc_command_server_restart = mock_rpc_command_server_restart

        result = await self.manager.rpc_command_server_restart_all()

        mock_rpc_command_server_restart.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in self.manager.instances.keys()
            ]
        )

        self.assertListEqual(
            server_ids,
            result.get('success'),
            'Did not return the correct list of server IDs',
        )

        self.assertListEqual(
            [],
            result.get('failure'),
            'Did not return the correct list of server IDs',
        )

    @utils.run_async
    async def test_server_restart_all_errors(self):
        """
        Check that we keep going if one of the servers errors out
        """

        server_ids = [
            'success0',
            'error0',
            'success1',
            'error1',
            'success2',
            'error2',
        ]

        self.manager.instances = {
            server_id: asynctest.Mock()
            for server_id in server_ids
        }

        def _restart_func(server_id):
            if server_id.startswith('success'):
                return server_id
            else:
                raise RuntimeError('Boom!')

        mock_server_restart = asynctest.CoroutineMock()
        mock_server_restart.side_effect = _restart_func

        self.manager.rpc_command_server_restart = mock_server_restart

        result = await self.manager.rpc_command_server_restart_all()

        self.assertListEqual(
            [
                server_id
                for server_id in self.manager.instances.keys()
                if server_id.startswith('success')
            ],
            result.get('success'),
            'The list of restarted server\'s did not match',
        )

        self.assertListEqual(
            [
                server_id
                for server_id in self.manager.instances.keys()
                if not server_id.startswith('success')
            ],
            result.get('failure'),
            'The list of failures did not match',
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

