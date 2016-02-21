"""
Tests for the mymcadmin.manager.Manager class
"""

import asyncio
import asyncio.subprocess
import json
import unittest

import asynctest

from ... import utils

from mymcadmin.manager import Manager
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

if __name__ == '__main__':
    unittest.main()

