"""
Tests for the JSON RPC client
"""

import asyncio
import json
import unittest
import unittest.mock

import asynctest
import nose

from mymcadmin.rpc import JsonRpcError, RpcClient

class TestRpcClient(unittest.TestCase):
    """
    Tests for the JSON RPC client
    """

    def setUp(self):
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        self.host   = 'localhost'
        self.port   = 8080
        self.client = RpcClient(self.host, self.port)

    @asynctest.patch('asyncio.open_connection')
    def test_execute_rpc_method(self, open_connection):
        """
        Tests that we can properly execute a method and return its response
        """

        writer_future = asyncio.Future()

        def _writer_func(request):
            writer_future.set_result(
                json.loads(
                    request.decode()
                )
            )

        mock_writer = asynctest.Mock(spec = asyncio.StreamWriter)
        mock_writer.write.side_effect = _writer_func

        mock_reader = asynctest.Mock(spec = asyncio.StreamReader)
        mock_reader.readline.return_value = json.dumps(
            {
                'jsonrpc': '2.0',
                'id': 1,
                'result': {
                    'the': 'thing',
                }
            }
        ).encode()

        open_connection.return_value = (mock_reader, mock_writer)

        client = RpcClient(self.host, self.port)
        client.start()

        response = client.execute_rpc_method(
            'testification',
            params = {
                'param0': 'test',
                'param1': 9001,
            },
        )

        client.stop()

        self.assertTrue(
            writer_future.done(),
            'Writer did not finish',
        )

        self.assertDictEqual(
            {
                'jsonrpc': '2.0',
                'method': 'testification',
                'params': {
                    'param0': 'test',
                    'param1': 9001,
                },
                'id': 1,
            },
            writer_future.result(),
            'Writer did not send the correct response',
        )

        self.assertDictEqual(
            {
                'the': 'thing',
            },
            response,
            'Client did not return the right response',
        )

        mock_writer.write_eof.assert_called_with()
        mock_writer.drain.assert_called_with()

    @nose.tools.raises(JsonRpcError)
    @asynctest.patch('asyncio.open_connection')
    def test_execute_rpc_method_error(self, open_connection):
        """
        Tests that we can properly execute a method and return its response
        """

        writer_future = asyncio.Future()

        def _writer_func(request):
            writer_future.set_result(
                json.loads(
                    request.decode()
                )
            )

        mock_writer = asynctest.Mock(spec = asyncio.StreamWriter)
        mock_writer.write.side_effect = _writer_func

        mock_reader = asynctest.Mock(spec = asyncio.StreamReader)
        mock_reader.readline.return_value = json.dumps(
            {
                'jsonrpc': '2.0',
                'id': 1,
                'error': {
                    'code': -32,
                    'message': 'things',
                }
            }
        ).encode()

        open_connection.return_value = (mock_reader, mock_writer)

        client = RpcClient(self.host, self.port)
        client.start()

        client.execute_rpc_method(
            'testification',
            params = {
                'param0': 'test',
                'param1': 9001,
            },
        )

    def test_list_servers(self):
        """
        Tests that the list_servers method works properly
        """

        self._test_method(
            'list_servers',
            result = ['test0', 'test1', 'test2'],
        )

    def test_server_start(self):
        """
        Tests that the server_start method works properly
        """

        self._test_method(
            'server_start',
            params = {'server_id': 'testification'},
            result = 'testification',
        )

    def test_server_start_all(self):
        """
        Tests that the server_start_all method works properly
        """

        self._test_method(
            'server_start_all',
            result = ['test0', 'test1', 'test2'],
        )

    def test_server_stop(self):
        """
        Tests that the server_stop method works properly
        """

        self._test_method(
            'server_stop',
            params = {'server_id': 'testification'},
            result = 'testification',
        )

    def test_server_stop_all(self):
        """
        Tests that the server_stop_all method works properly
        """

        self._test_method(
            'server_stop_all',
            result = ['test0', 'test1', 'test2'],
        )

    def test_server_restart(self):
        """
        Tests that the server_restart method works properly
        """

        self._test_method(
            'server_restart',
            params = {'server_id': 'testification'},
            result = 'testification',
        )

    def test_server_restart_all(self):
        """
        Tests that the server_restart_all method works properly
        """

        self._test_method(
            'server_restart_all',
            result = ['test0', 'test1', 'test2'],
        )

    def test_shutdown(self):
        """
        Tests that the shutdown method works properly
        """

        self._test_method(
            'shutdown',
            result = ['test0', 'test1', 'test2'],
        )

    def test_context_manager(self):
        """
        Test that we can use the client as a context manager
        """

        mock_start = unittest.mock.Mock()
        mock_stop  = unittest.mock.Mock()

        self.client.start = mock_start
        self.client.stop  = mock_stop

        with self.client as client:
            self.assertEqual(
                self.client,
                client,
                'Context manager did not return the right object',
            )

        self.assertTrue(
            mock_start.called,
            'Start was not called',
        )

        self.assertTrue(
            mock_stop.called,
            'Stop was not called',
        )

    @nose.tools.raises(JsonRpcError)
    @asynctest.patch('asyncio.open_connection')
    def test_error_response(self, open_connection):
        """
        Test that we handle errors from the server
        """

        mock_reader = asynctest.Mock(spec = asyncio.StreamReader)
        mock_reader.readline.return_value = json.dumps(
            {
                'jsonrpc': '2.0',
                'id':      1,
                'error':   {
                    'message': 'blue screen of death',
                    'code':    -9001,
                },
            }
        ).encode()

        mock_writer = asynctest.Mock(spec = asyncio.StreamWriter)

        open_connection.return_value = (mock_reader, mock_writer)

        self.client.start()

        self.client.shutdown()

        self.client.stop()

    def _test_method(self, method, params = None, result = None):
        with asynctest.patch('mymcadmin.rpc.RpcClient.execute_rpc_method') as \
                execute_rpc_method:
            execute_rpc_method.return_value = result

            client = RpcClient(self.host, self.port)

            method_func = getattr(client, method)

            if params is not None:
                response = method_func(**params)

                execute_rpc_method.assert_called_with(method, params)
            else:
                response = method_func()

                execute_rpc_method.assert_called_with(method)

            self.assertEqual(
                result,
                response,
                'Client did not return the expected result',
            )

if __name__ == '__main__':
    unittest.main()

