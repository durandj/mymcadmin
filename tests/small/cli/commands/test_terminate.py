import click.testing
import unittest
import unittest.mock

from mymcadmin.cli import mymcadmin as mma_command

class TestTerminate(unittest.TestCase):
	def setUp(self):
		self.cli_runner = click.testing.CliRunner()

	@unittest.mock.patch('mymcadmin.rpc.RpcClient')
	@unittest.mock.patch('mymcadmin.server.Server')
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.config.Config')
	def test_command(self, config, exists, server, rpc_client):
		exists = True

		server.return_value = server
		server.socket_settings = ('tcp', 'localhost', 8000)

		rpc_client.return_value = rpc_client
		rpc_client.__enter__.return_value = rpc_client

		result = self.cli_runner.invoke(mma_command, ['terminate', 'test'])

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate properly',
		)

		rpc_client.assert_called_with('localhost', 8000)
		rpc_client.terminate.assert_called_with()

	@unittest.mock.patch('mymcadmin.rpc.RpcClient')
	@unittest.mock.patch('mymcadmin.server.Server')
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.config.Config')
	def test_command_fail(self, config, exists, server, rpc_client):
		exists = True

		server.return_value = server
		server.socket_settings = ('tcp', 'localhost', 8000)

		rpc_client.return_value = rpc_client
		rpc_client.__enter__.return_value = rpc_client
		rpc_client.terminate.side_effect = RuntimeError

		result = self.cli_runner.invoke(mma_command, ['terminate', 'test'])

		self.assertEqual(
			1,
			result.exit_code,
			'Command did not terminate properly',
		)

class TestTerminateAll(unittest.TestCase):
	def setUp(self):
		self.cli_runner = click.testing.CliRunner()

	@unittest.mock.patch('mymcadmin.rpc.RpcClient')
	@unittest.mock.patch('mymcadmin.server.Server')
	@unittest.mock.patch('mymcadmin.config.Config')
	def test_command(self, config, server, rpc_client):
		server_names = [
			'test0',
			'test1',
			'test2',
			'test3',
		]

		servers = [
			unittest.mock.Mock(
				name            = name,
				socket_settings = ('tcp', 'localhost', 8000),
			)
			for name in server_names
		]

		server.list_all.return_value = server_names
		server.side_effect = servers

		rpc_client.return_value = rpc_client
		rpc_client.__enter__.return_value = rpc_client

		result = self.cli_runner.invoke(mma_command, ['terminate_all'])

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate properly',
		)

		self.assertEqual(
			len(servers),
			rpc_client.terminate.call_count,
			'Not all servers were terminated',
		)

if __name__ == '__main__':
	unittest.main()

