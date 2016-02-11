import click.testing
import nose
import os
import unittest
import unittest.mock

from mymcadmin import errors
from mymcadmin.cli import mymcadmin as mma_command
from mymcadmin.cli.commands.start import start_server_daemon

class TestStart(unittest.TestCase):
	def setUp(self):
		self.cli_runner = click.testing.CliRunner()

	@unittest.mock.patch('multiprocessing.Process')
	@unittest.mock.patch('mymcadmin.server.Server')
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.config.Config')
	def test_command(self, config, exists, server, process):
		exists.side_effect = lambda p: p != 'test'

		server.return_value = server
		server.name = 'test'
		server.pid_file = 'test'

		process.return_value = process

		result = self.cli_runner.invoke(mma_command, ['start', 'vanilla'])

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate properly',
		)

		process.assert_called_with(
			target = start_server_daemon,
			args   = (server, None, None),
		)

		process.start.assert_called_with()
		process.join.assert_called_with()

	@unittest.mock.patch('multiprocessing.Process')
	@unittest.mock.patch('mymcadmin.server.Server')
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.config.Config')
	def test_command_fail(self, config, exists, server, process):
		exists.side_effect = lambda p: p != 'test'

		server.return_value = server
		server.name = 'test'
		server.pid_file = 'test'

		process.side_effect = RuntimeError('Boom!')

		result = self.cli_runner.invoke(mma_command, ['start', 'test'])

		self.assertEqual(
			1,
			result.exit_code,
			'Command did not terminate properly',
		)

	@unittest.mock.patch('mymcadmin.rpc.RpcClient')
	@unittest.mock.patch('mymcadmin.server.Server')
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.config.Config')
	def test_command_manager_started(self, config, exists, server, rpc_client):
		exists.return_value = True

		server.return_value = server
		server.name = 'test'
		server.socket_settings = ('tcp', 'localhost', 8000)

		rpc_client.return_value = rpc_client
		rpc_client.__enter__.return_value = rpc_client

		result = self.cli_runner.invoke(mma_command, ['start', 'test'])

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate properly',
		)

		rpc_client.server_start.assert_called_with()
		rpc_client.assert_called_with('localhost', 8000)

	@unittest.mock.patch('multiprocessing.Process')
	@unittest.mock.patch('mymcadmin.server.Server')
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.config.Config')
	def test_command_user(self, config, exists, server, process):
		exists.side_effect = lambda p: p != 'test'

		server.return_value = server
		server.name = 'test'
		server.pid_file = 'test'

		process.return_value = process

		result = self.cli_runner.invoke(
			mma_command,
			['start', 'vanilla', '--user', os.getuid()],
		)

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate properly',
		)

		process.assert_called_with(
			target = start_server_daemon,
			args   = (server, os.getuid(), None),
		)

		process.start.assert_called_with()
		process.join.assert_called_with()

	@unittest.mock.patch('multiprocessing.Process')
	@unittest.mock.patch('mymcadmin.server.Server')
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.config.Config')
	def test_command_group(self, config, exists, server, process):
		exists.side_effect = lambda p: p != 'test'

		server.return_value = server
		server.name = 'test'
		server.pid_file = 'test'

		process.return_value = process

		result = self.cli_runner.invoke(
			mma_command,
			['start', 'vanilla', '--group', os.getgid()],
		)

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate properly',
		)

		process.assert_called_with(
			target = start_server_daemon,
			args   = (server, None, os.getgid()),
		)

		process.start.assert_called_with()
		process.join.assert_called_with()

	@unittest.mock.patch('mymcadmin.manager.Manager')
	@unittest.mock.patch('daemon.pidfile.PIDLockFile')
	@unittest.mock.patch('daemon.DaemonContext')
	@unittest.mock.patch('builtins.open')
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.server.Server')
	def test_start_server_daemon(self, server, exists, open, daemon, pidfile, manager):
		server.return_value = server
		server.admin_log = 'test.txt'
		server.pid_file  = 'test.pid'
		server.path      = 'home'

		exists.return_value = False

		open.return_value = open

		pidfile.return_value = pidfile

		manager.return_value = manager

		start_server_daemon(server, None, None)

		open.assert_called_with('test.txt', 'a')

		daemon.assert_called_with(
			detach_process    = True,
			gid               = None,
			pidfile           = pidfile,
			stdout            = open,
			stderr            = open,
			uid               = None,
			working_directory = 'home',
		)

		manager.assert_called_with(server)
		manager.run.assert_called_with()

	@nose.tools.raises(errors.MyMCAdminError)
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.server.Server')
	def test_start_server_daemon_fail(self, server, exists):
		exists.return_value = True

		start_server_daemon(server, None, None)

class TestStartAll(unittest.TestCase):
	def setUp(self):
		self.cli_runner = click.testing.CliRunner()

	@unittest.mock.patch('multiprocessing.Process')
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.server.Server')
	@unittest.mock.patch('mymcadmin.config.Config')
	def test_command(self, config, server, exists, process):
		server.list_all.return_value = [
			'test0',
			'test1',
			'test2',
			'test4',
		]

		servers = [
			unittest.mock.Mock(),
			unittest.mock.Mock(),
			unittest.mock.Mock(),
			unittest.mock.Mock(),
		]

		server.side_effect = servers
		for srv in servers:
			srv.name     = 'test'
			srv.pid_file = 'test'

		exists.side_effect = lambda p: p != 'test'

		process.return_value = process

		result = self.cli_runner.invoke(mma_command, ['start_all'])

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate properly',
		)

		for srv in servers:
			process.assert_has_calls(
				[
					unittest.mock.call(
						target = start_server_daemon,
						args   = (srv, None, None),
					)
				]
			)

		self.assertEqual(
			len(servers),
			process.start.call_count,
			'Not all servers were started',
		)

		self.assertEqual(
			len(servers),
			process.join.call_count,
		)

	@unittest.mock.patch('multiprocessing.Process')
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.server.Server')
	@unittest.mock.patch('mymcadmin.config.Config')
	def test_command_user(self, config, server, exists, process):
		server.list_all.return_value = [
			'test0',
			'test1',
			'test2',
			'test4',
		]

		servers = [
			unittest.mock.Mock(),
			unittest.mock.Mock(),
			unittest.mock.Mock(),
			unittest.mock.Mock(),
		]

		server.side_effect = servers
		for srv in servers:
			srv.name     = 'test'
			srv.pid_file = 'test'

		exists.side_effect = lambda p: p != 'test'

		process.return_value = process

		result = self.cli_runner.invoke(
			mma_command,
			['start_all', '--user', os.getuid()],
		)

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate properly',
		)

		for srv in servers:
			process.assert_has_calls(
				[
					unittest.mock.call(
						target = start_server_daemon,
						args   = (srv, os.getuid(), None),
					)
				]
			)

		self.assertEqual(
			len(servers),
			process.start.call_count,
			'Not all servers were started',
		)

		self.assertEqual(
			len(servers),
			process.join.call_count,
		)

	@unittest.mock.patch('multiprocessing.Process')
	@unittest.mock.patch('os.path.exists')
	@unittest.mock.patch('mymcadmin.server.Server')
	@unittest.mock.patch('mymcadmin.config.Config')
	def test_command_group(self, config, server, exists, process):
		server.list_all.return_value = [
			'test0',
			'test1',
			'test2',
			'test4',
		]

		servers = [
			unittest.mock.Mock(),
			unittest.mock.Mock(),
			unittest.mock.Mock(),
			unittest.mock.Mock(),
		]

		server.side_effect = servers
		for srv in servers:
			srv.name     = 'test'
			srv.pid_file = 'test'

		exists.side_effect = lambda p: p != 'test'

		process.return_value = process

		result = self.cli_runner.invoke(
			mma_command,
			['start_all', '--group', os.getgid()],
		)

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate properly',
		)

		for srv in servers:
			process.assert_has_calls(
				[
					unittest.mock.call(
						target = start_server_daemon,
						args   = (srv, None, os.getgid()),
					)
				]
			)

		self.assertEqual(
			len(servers),
			process.start.call_count,
			'Not all servers were started',
		)

		self.assertEqual(
			len(servers),
			process.join.call_count,
		)

if __name__ == '__main__':
	unittest.main()

