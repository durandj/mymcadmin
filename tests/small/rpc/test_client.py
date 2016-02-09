import asyncio
import asynctest
import json
import nose
import unittest
import unittest.mock

from mymcadmin.rpc import JsonRpcError, RpcClient

class TestRpcClient(unittest.TestCase):
	def setUp(self):
		self.event_loop = asyncio.new_event_loop()
		asyncio.set_event_loop(self.event_loop)

		self.host   = 'localhost'
		self.port   = 8080
		self.client = RpcClient(self.host, self.port)

	@asynctest.patch('asyncio.open_connection')
	def test_send_command(self, open_connection):
		commands = {
			'serverRestart': self.client.server_restart,
			'serverStart':   self.client.server_start,
			'serverStop':    self.client.server_stop,
			'terminate':     self.client.terminate,
		}

		mock_reader = asynctest.Mock(spec = asyncio.StreamReader)
		mock_reader.read.return_value = json.dumps(
			{
				'jsonrpc': '2.0',
				'id':      1,
				'result':  {'success': True},
			}
		).encode()

		mock_writer = asynctest.Mock(spec = asyncio.StreamWriter)

		open_connection.return_value = (mock_reader, mock_writer)

		self.client.run()

		open_connection.assert_called_with(
			self.host,
			self.port,
			loop = self.event_loop,
		)

		for name, command in commands.items():
			open_connection.reset_mock()
			mock_reader.reset_mock()
			mock_writer.reset_mock()

			mock_writer_future = asyncio.Future()
			mock_writer.write.side_effect = mock_writer_future.set_result

			command()

			self.assertDictEqual(
				{
					'jsonrpc': '2.0',
					'method':  name,
					'params':  {},
					'id':      1,
				},
				json.loads(mock_writer_future.result().decode()),
				'The writer was not given the correct request',
			)

			self.assertTrue(
				mock_reader.read.called,
				'Client did not try to read the server response',
			)

		self.client.stop()

	def test_context_handler(self):
		mock_run  = unittest.mock.Mock()
		mock_stop = unittest.mock.Mock()

		self.client.run  = mock_run
		self.client.stop = mock_stop

		with self.client as client:
			self.assertEqual(
				self.client,
				client,
				'Context manager did not return the right object',
			)

		self.assertTrue(
			mock_run.called,
			'Run was not called',
		)

		self.assertTrue(
			mock_stop.called,
			'Stop was not called',
		)

	@nose.tools.raises(JsonRpcError)
	@asynctest.patch('asyncio.open_connection')
	def test_error_response(self, open_connection):
		mock_reader = asynctest.Mock(spec = asyncio.StreamReader)
		mock_reader.read.return_value = json.dumps(
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

		self.client.run()

		self.client.terminate()

		self.client.stop()

if __name__ == '__main__':
	unittest.main()

