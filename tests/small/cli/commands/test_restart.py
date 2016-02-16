"""
Tests for the CLI restart commands
"""

import unittest
import unittest.mock

from .... import utils

from mymcadmin.cli import mymcadmin as mma_command

class TestRestart(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the restart command
    """

    def setUp(self):
        super(TestRestart, self).setUp()

        self.host        = 'localhost'
        self.port        = 8080

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_defaults(self, config):
        """
        Tests that the command works properly with defaults
        """

        config.return_value = config
        config.rpc = None

        self._run_test('localhost', 2323)

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_config(self, config):
        """
        Tests that the command works with the config options
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
        Tests that the command works with the command options
        """

        config.return_value = config
        config.rpc = None

        self._run_test(
            'example.com',
            8080,
            ['--host', 'example.com', '--port', 8080],
        )

    @unittest.mock.patch('mymcadmin.rpc.RpcClient')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_fail(self, config, exists, rpc_client):
        """
        Tests that the command handles restart failures
        """

        config.return_value = config
        config.rpc = None

        exists.return_value = True

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client
        rpc_client.server_restart.side_effect = RuntimeError

        result = self.cli_runner.invoke(mma_command, ['restart', 'test'])

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate successfully',
        )

    def _run_test(self, expected_host, expected_port, params = None):
        if params is None:
            params = []

        with unittest.mock.patch('os.path.exists') as exists, \
                unittest.mock.patch('mymcadmin.rpc.RpcClient') as rpc_client:
            exists.return_value = True

            rpc_client.return_value = rpc_client
            rpc_client.__enter__.return_value = rpc_client

            result = self.cli_runner.invoke(
                mma_command,
                ['restart', 'test'] + params,
            )

            if result.exit_code != 0:
                print(result.output)

            self.assertEqual(
                0,
                result.exit_code,
                'Command did not terminate successfully',
            )

            rpc_client.assert_called_with(
                expected_host,
                expected_port,
            )

            rpc_client.server_restart.assert_called_with('test')

class TestRestartAll(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the restart_all command
    """

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_default(self, config):
        """
        Tests that the command works properly with defaults
        """

        config.return_value = config
        config.rpc = None

        self._run_test('localhost', 2323)

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_config(self, config):
        """
        Test that the command uses the config
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
        Test that the command uses the options
        """

        config.return_value = config
        config.rpc = None

        self._run_test(
            'example.com',
            8080,
            [
                '--host', 'example.com',
                '--port', 8080,
            ],
        )

    @unittest.mock.patch('mymcadmin.rpc.RpcClient')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_fail(self, config, rpc_client):
        """
        Test that the command handles exceptions
        """

        config.return_value = config
        config.rpc = None

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client
        rpc_client.server_restart_all.side_effect = RuntimeError('Boom!')

        result = self.cli_runner.invoke(mma_command, ['restart_all'])

        if result.exit_code != 1:
            print(result.output)

        self.assertEqual(
            1,
            result.exit_code,
            'The command did not terminate properly',
        )

    def _run_test(self, expected_host, expected_port, params = None):
        if params is None:
            params = []

        server_ids = [
            'server0',
            'server1',
            'server2',
            'server3',
            'server4',
        ]

        with unittest.mock.patch('mymcadmin.rpc.RpcClient') as rpc_client, \
                unittest.mock.patch('mymcadmin.cli.commands.restart.success') as success:
            rpc_client.return_value = rpc_client
            rpc_client.__enter__.return_value = rpc_client
            rpc_client.server_restart_all.return_value = server_ids

            result = self.cli_runner.invoke(
                mma_command,
                ['restart_all'] + params,
            )

            if result.exit_code != 0:
                print(result.output)

            self.assertEqual(
                0,
                result.exit_code,
                'Command did not terminate properly',
            )

            rpc_client.assert_called_with(expected_host, expected_port)

            rpc_client.server_restart_all.assert_called_with()

            success.assert_has_calls(
                [
                    unittest.mock.call(
                        '{} successfully restarted'.format(server_id)
                    )
                    for server_id in server_ids
                ]
            )

if __name__ == '__main__':
    unittest.main()

