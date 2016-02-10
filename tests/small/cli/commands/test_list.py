import click.testing
import os.path
import unittest
import unittest.mock

from mymcadmin.cli.base import mymcadmin as mma_command
from mymcadmin.cli.commands.list import list_servers, list_versions

class TestListServers(unittest.TestCase):
	def setUp(self):
		self.cli_runner = click.testing.CliRunner()
		self.root         = 'root'
		self.server_names = ['server1', 'server2', 'server3']
		self.servers      = [
			os.path.join(self.root, s)
			for s in self.server_names
		]

	@unittest.mock.patch('click.echo')
	@unittest.mock.patch('mymcadmin.server.Server.list_all')
	def test_command(self, list_all, echo):
		list_all.return_value = self.servers

		result = self.cli_runner.invoke(mma_command, ['list_servers'])

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate successfully',
		)

		self.assertEqual(
			len(self.server_names),
			echo.call_count,
			'Servers were not all printed out',
		)

		echo.assert_has_calls(
			[
				unittest.mock.call(name)
				for name in self.server_names
			]
		)

class TestListVersions(unittest.TestCase):
	def setUp(self):
		self.cli_runner = click.testing.CliRunner()

	@unittest.mock.patch('click.echo')
	@unittest.mock.patch('mymcadmin.server.Server.list_versions')
	def test_command(self, list_versions, echo):
		list_versions.return_value = {
			'latest': {
				'snapshot': 'my_snapshot',
				'release':  'my_release',
			},
			'versions': [
				{'id': 'my_snapshot'},
				{'id': 'my_release'},
				{'id': 'my_beta'},
				{'id': 'my_alpha'},
			],
		}

		result = self.cli_runner.invoke(mma_command, ['list_versions'])

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate successfully',
		)

		echo.assert_has_calls(
			[
				unittest.mock.call('Snapshot: my_snapshot'),
				unittest.mock.call('Release:  my_release'),
				unittest.mock.call('my_snapshot'),
				unittest.mock.call('my_release'),
				unittest.mock.call('my_beta'),
				unittest.mock.call('my_alpha'),
			]
		)

	@unittest.mock.patch('click.echo')
	@unittest.mock.patch('mymcadmin.server.Server.list_versions')
	def test_command_no_snapshots(self, list_versions, echo):
		list_versions.return_value = {
			'latest': {
				'snapshot': '',
				'release':  'my_release',
			},
			'versions': [
				{'id': 'my_release'},
				{'id': 'my_beta'},
				{'id': 'my_alpha'},
			],
		}

		result = self.cli_runner.invoke(
			mma_command,
			['list_versions', '--no-snapshots'],
		)

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate successfully',
		)

		echo.assert_has_calls(
			[
				unittest.mock.call('Snapshot: '),
				unittest.mock.call('Release:  my_release'),
				unittest.mock.call('my_release'),
				unittest.mock.call('my_beta'),
				unittest.mock.call('my_alpha'),
			]
		)

		list_versions.assert_called_with(
			snapshots = False,
			releases  = True,
			betas     = True,
			alphas    = True,
		)

	@unittest.mock.patch('click.echo')
	@unittest.mock.patch('mymcadmin.server.Server.list_versions')
	def test_command_no_releases(self, list_versions, echo):
		list_versions.return_value = {
			'latest': {
				'snapshot': 'my_snapshot',
				'release':  '',
			},
			'versions': [
				{'id': 'my_snapshot'},
				{'id': 'my_beta'},
				{'id': 'my_alpha'},
			],
		}

		result = self.cli_runner.invoke(
			mma_command,
			['list_versions', '--no-releases'],
		)

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate successfully',
		)

		echo.assert_has_calls(
			[
				unittest.mock.call('Snapshot: my_snapshot'),
				unittest.mock.call('Release:  '),
				unittest.mock.call('my_snapshot'),
				unittest.mock.call('my_beta'),
				unittest.mock.call('my_alpha'),
			]
		)

		list_versions.assert_called_with(
			snapshots = True,
			releases  = False,
			betas     = True,
			alphas    = True,
		)

	@unittest.mock.patch('click.echo')
	@unittest.mock.patch('mymcadmin.server.Server.list_versions')
	def test_command_no_betas(self, list_versions, echo):
		list_versions.return_value = {
			'latest': {
				'snapshot': 'my_snapshot',
				'release':  'my_release',
			},
			'versions': [
				{'id': 'my_snapshot'},
				{'id': 'my_release'},
				{'id': 'my_alpha'},
			],
		}

		result = self.cli_runner.invoke(
			mma_command,
			['list_versions', '--no-betas'],
		)

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate successfully',
		)

		echo.assert_has_calls(
			[
				unittest.mock.call('Snapshot: my_snapshot'),
				unittest.mock.call('Release:  my_release'),
				unittest.mock.call('my_snapshot'),
				unittest.mock.call('my_release'),
				unittest.mock.call('my_alpha'),
			]
		)

		list_versions.assert_called_with(
			snapshots = True,
			releases  = True,
			betas     = False,
			alphas    = True,
		)

	@unittest.mock.patch('click.echo')
	@unittest.mock.patch('mymcadmin.server.Server.list_versions')
	def test_command_no_alphas(self, list_versions, echo):
		list_versions.return_value = {
			'latest': {
				'snapshot': 'my_snapshot',
				'release':  'my_release',
			},
			'versions': [
				{'id': 'my_snapshot'},
				{'id': 'my_release'},
				{'id': 'my_beta'},
			],
		}

		result = self.cli_runner.invoke(
			mma_command,
			['list_versions', '--no-alphas'],
		)

		self.assertEqual(
			0,
			result.exit_code,
			'Command did not terminate successfully',
		)

		echo.assert_has_calls(
			[
				unittest.mock.call('Snapshot: my_snapshot'),
				unittest.mock.call('Release:  my_release'),
				unittest.mock.call('my_snapshot'),
				unittest.mock.call('my_release'),
				unittest.mock.call('my_beta'),
			]
		)

		list_versions.assert_called_with(
			snapshots = True,
			releases  = True,
			betas     = True,
			alphas    = False,
		)

if __name__ == '__main__':
	unittest.main()

