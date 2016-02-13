"""
Tests for the mymcadmin.manager.Manager class
"""

import asyncio
import asyncio.subprocess
import json
import unittest

import asynctest

from .. import utils

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

    def test_constructor(self):
        """
        Check that the constructor starts the handlers properly
        """

        manager = Manager(self.host, self.port, self.root)

        self.assertTrue(
            len(manager.rpc_dispatcher) > 0,
            'Dispatcher was not initialized with handlers',
        )

    @asynctest.patch('mymcadmin.manager.Manager.handle_network_connection')
    @asynctest.patch('asyncio.start_server')
    def test_run(self, start_server, handle_network_connection):
        """
        Check that the run function starts and stops the event loop
        """

        mock_event_loop = asynctest.Mock(asyncio.BaseEventLoop)
        asyncio.set_event_loop(mock_event_loop)

        manager = Manager(self.host, self.port, self.root)
        manager.run()

        asyncio.set_event_loop(self.event_loop)

        start_server.assert_called_with(
            handle_network_connection,
            self.host,
            self.port,
            loop = mock_event_loop,
        )

        mock_event_loop.run_forever.assert_called_with()
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

        req = (json.dumps(
            {
                'jsonrpc': '2.0',
                'method':  'test',
                'params':  {'im': 'a test'},
                'id':      1,
            }
        ) + '\n').encode()
        mock_reader.readline.return_value = req

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

    @utils.run_async
    async def test_rpc_shutdown_running_proc(self):
        """
        Check that the shutdown command stops any running server instances
        """

        instance_names = ['test0', 'test1', 'test2', 'test3']
        instances      = {}
        for name in instance_names:
            mock      = asynctest.Mock(spec = asyncio.subprocess.Process)
            mock.name = name

            instances[name] = mock

        mock_event_loop = asynctest.Mock(spec = asyncio.BaseEventLoop)

        mock_server_stop = asynctest.CoroutineMock()

        manager = Manager(
            self.host,
            self.port,
            self.root,
            event_loop = mock_event_loop,
        )
        manager.instances = {
            name: asynctest.Mock(spec = asyncio.subprocess.Process)
            for name in instance_names
        }
        manager.rpc_command_server_stop = mock_server_stop
        manager.rpc_command_server_stop.side_effect = instance_names

        result = await manager.rpc_command_shutdown()

        self.assertEqual(
            instance_names,
            result,
            'Return message did not match',
        )

        mock_server_stop.assert_has_calls(
            [
                unittest.mock.call(name)
                for name in instances.keys()
            ]
        )

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
        mock_server.name = 'test'
        mock_server.start = asynctest.CoroutineMock()
        mock_server.start.return_value = mock_proc_func()

        manager = Manager(
            self.host,
            self.port,
            self.root,
            event_loop = mock_event_loop,
        )

        await manager.start_server_proc(mock_server)

        mock_server.start.assert_called_with()
        mock_proc.wait.assert_called_with()

if __name__ == '__main__':
    unittest.main()

