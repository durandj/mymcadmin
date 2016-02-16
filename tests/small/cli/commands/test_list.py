"""
Tests for the CLI list commands
"""

import os.path
import unittest
import unittest.mock

from .... import utils

from mymcadmin.cli.base import mymcadmin as mma_command

class TestListServers(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the list_servers command
    """

    def setUp(self):
        super(TestListServers, self).setUp()

        self.root         = 'root'
        self.server_names = ['server1', 'server2', 'server3']
        self.servers      = [
            os.path.join(self.root, s)
            for s in self.server_names
        ]

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_default(self, config):
        """
        tests that the command works with defaults
        """

        config.return_value = config
        config.rpc = None

        self._run_test('localhost', 2323)

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_config(self, config):
        """
        Test that the command uses the configuration options
        """

        config.return_value = config
        config.rpc = {
            'host': 'example.com',
            'port': 8080,
        }

        self._run_test('example.com', 8080)

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_options(self, config):
        """
        Tests that the command uses the given options
        """

        config.return_value = config
        config.rpc = None

        self._run_test(
            'example.com',
            8080,
            ['--host', 'example.com', '--port', 8080],
        )

    def _run_test(self, expected_host, expected_port, params = None):
        if params is None:
            params = []

        with unittest.mock.patch('mymcadmin.rpc.RpcClient') as rpc_client, \
            unittest.mock.patch('click.echo') as echo:
            rpc_client.return_value = rpc_client
            rpc_client.__enter__.return_value = rpc_client
            rpc_client.list_servers.return_value = self.server_names

            result = self.cli_runner.invoke(mma_command, ['list_servers'] + params)

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

            rpc_client.assert_called_with(
                expected_host,
                expected_port,
            )

class TestListVersions(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the list_versions command
    """

    @unittest.mock.patch('click.echo')
    @unittest.mock.patch('mymcadmin.server.Server.list_versions')
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command(self, list_versions, echo):
        """
        Tests that the command works properly with default options
        """

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
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command_no_snapshots(self, list_versions, echo):
        """
        Tests that the command filters out snapshots
        """

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
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command_no_releases(self, list_versions, echo):
        """
        Tests that the command filters releases
        """

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
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command_no_betas(self, list_versions, echo):
        """
        Tests that the command filters betas
        """

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
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command_no_alphas(self, list_versions, echo):
        """
        Tests that the command filters alphas
        """

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

