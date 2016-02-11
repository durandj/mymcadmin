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

        self.socket_type = 'tcp'
        self.host        = 'localhost'
        self.port        = 8080

        self.socket_settings = (self.socket_type, self.host, self.port)

        self.mock_server = asynctest.Mock(spec = Server)
        self.mock_server.socket_settings = self.socket_settings

    def tearDown(self):
        self.event_loop.close()

    def test_constructor(self):
        """
        Check that the constructor starts the handlers properly
        """

        manager = Manager(self.mock_server)

        self.assertTrue(
            len(manager.rpc_dispatcher) > 0,
            'Dispatcher was not initialized with handlers',
        )

    @asynctest.patch('mymcadmin.manager.Manager._handle_proc')
    @asynctest.patch('mymcadmin.manager.Manager._handle_network_connection')
    @asynctest.patch('asyncio.start_server')
    def test_run(self, start_server, _handle_network_connection, _handle_proc):
        """
        Check that the run function starts and stops the event loop
        """

        mock_event_loop = asynctest.Mock(asyncio.BaseEventLoop)
        asyncio.set_event_loop(mock_event_loop)

        manager = Manager(self.mock_server)
        manager.run()

        asyncio.set_event_loop(self.event_loop)

        start_server.assert_called_with(
            _handle_network_connection,
            self.host,
            self.port,
            loop = mock_event_loop,
        )

        _handle_proc.assert_called_with()
        mock_event_loop.run_forever.assert_called_with()
        mock_event_loop.close.assert_called_with()

    @utils.run_async
    async def test_handle_network_connection(self):
        """
        Check that the network handling handles all of the commands properly
        """

        with asynctest.patch('mymcadmin.manager.Manager._handle_proc'):
            commands = {
                'serverRestart': 'restarting server',
                'serverStart':   'starting server',
                'serverStop':    'stopping server',
                'terminate':      'terminating manager',
            }

            mock_event_loop = asynctest.Mock(spec = asyncio.BaseEventLoop)
            mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

            mock_reader = asynctest.Mock(spec = asyncio.StreamReader)

            mock_writer = asynctest.Mock(spec = asyncio.StreamWriter)
            mock_writer.get_extra_info.return_value = '127.0.0.1'

            manager = Manager(self.mock_server, mock_event_loop)
            manager.proc = mock_proc

            for name, response in commands.items():
                mock_event_loop.reset_mock()
                mock_reader.reset_mock()
                mock_writer.reset_mock()

                response_future = asyncio.Future()
                mock_writer.write.side_effect = response_future.set_result

                req = (json.dumps(
                    {
                        'jsonrpc': '2.0',
                        'method':  name,
                        'params':  {},
                        'id':      1,
                    }
                ) + '\n').encode()
                mock_reader.readline.return_value = req

                await manager._handle_network_connection(mock_reader, mock_writer)

                self.assertTrue(
                    response_future.done(),
                    'Response was never sent',
                )

                resp = json.loads(response_future.result().decode())
                self.assertDictEqual(
                    {
                        'jsonrpc': '2.0',
                        'id':      1,
                        'result':  response,
                    },
                    resp,
                )

    @utils.run_async
    async def test_terminate_running_proc(self):
        """
        Check that the terminate command stops the proc if its running
        """

        with asynctest.patch('mymcadmin.manager.Manager._handle_network_connection'):
            with asynctest.patch('mymcadmin.manager.Manager._handle_proc'):
                mock_event_loop = asynctest.Mock(spec = asyncio.BaseEventLoop)

                mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)
                mock_proc.returncode = None

                mock_server_stop = asynctest.CoroutineMock()

                manager = Manager(self.mock_server, event_loop = mock_event_loop)
                manager.proc = mock_proc
                manager._rpc_command_server_stop = mock_server_stop

                message = await manager._rpc_command_terminate()

                self.assertEqual(
                    'terminating manager',
                    message,
                    'Return message did not match',
                )

                mock_server_stop.assert_called_with()
                mock_proc.wait.assert_called_with()

    @utils.run_async
    async def test_handle_proc(self):
        """
        Check that the proc is started and waited for properly
        """

        with asynctest.patch('mymcadmin.manager.Manager._handle_network_connection'):
            mock_event_loop = asynctest.Mock(spec = asyncio.BaseEventLoop)
            mock_event_loop.run_until_complete.side_effect = \
                    self.event_loop.run_until_complete

            mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

            mock_proc_func = asynctest.CoroutineMock()
            mock_proc_func.return_value = mock_proc

            self.mock_server.start.return_value = mock_proc_func()

            manager = Manager(self.mock_server, event_loop = mock_event_loop)
            manager.run()

            self.mock_server.start.assert_called_with()
            mock_proc.wait.assert_called_with()

if __name__ == '__main__':
    unittest.main()

