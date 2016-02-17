"""
Tests for the CLI stop commands
"""

import unittest
import unittest.mock

from .... import utils

from mymcadmin.cli import mymcadmin as mma_command

class TestStop(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the stop command
    """

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_default(self, config):
        """
        Tests that the command functions properly with defaults
        """

        config.return_value = config
        config.rpc = None

        self._run_test('localhost', 2323)

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_config(self, config):
        """
        Tests that the command uses the config options
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
        Tests that the command uses the command line options
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
        Tests that the command handles exceptions
        """

        config.return_value = config
        config.rpc = None

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client
        rpc_client.server_stop.side_effect = RuntimeError('Boom!')

        result = self.cli_runner.invoke(mma_command, ['stop', 'test'])

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

    def _run_test(self, expected_host, expected_port, params = None):
        if params is None:
            params = []

        with unittest.mock.patch('mymcadmin.rpc.RpcClient') as rpc_client:
            rpc_client.return_value = rpc_client
            rpc_client.__enter__.return_value = rpc_client

            result = self.cli_runner.invoke(
                mma_command,
                ['stop', 'test'] + params,
            )

            if result.exit_code != 0:
                print(result.output)

            self.assertEqual(
                0,
                result.exit_code,
                'The command did not terminate properly',
            )

            rpc_client.assert_called_with(expected_host, expected_port)

            rpc_client.server_stop.assert_called_with('test')

class TestStopAll(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the stop_all command
    """

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_defaults(self, config):
        """
        Tests that the command functions properly with defaults
        """

        config.return_value = config
        config.rpc = None

        self._run_test('localhost', 2323)

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_config(self, config):
        """
        Tests that the command uses the config options
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
        Tests that the command uses the command line options
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
        Tests that the command handles exceptions
        """

        config.return_value = config
        config.rpc = None

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client
        rpc_client.server_stop_all.side_effect = RuntimeError('Boom!')

        result = self.cli_runner.invoke(mma_command, ['stop_all'])

        if result.exit_code != 1:
            print(result.output)

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

    def _run_test(self, expected_host, expected_port, params = None):
        if params is None:
            params = []

        success_ids = [
            'server0',
            'server1',
            'server2',
            'server3',
            'server4',
        ]

        error_ids = [
            'error0',
            'error1',
        ]

        with unittest.mock.patch('mymcadmin.rpc.RpcClient') as rpc_client, \
             unittest.mock.patch('mymcadmin.cli.commands.stop.success') as success, \
             unittest.mock.patch('mymcadmin.cli.commands.stop.error') as error:
            rpc_client.return_value = rpc_client
            rpc_client.__enter__.return_value = rpc_client
            rpc_client.server_stop_all.return_value = {
                'success': success_ids,
                'failure': error_ids,
            }

            result = self.cli_runner.invoke(
                mma_command,
                ['stop_all'] + params,
            )

            if result.exit_code != 0:
                print(result.output)

            self.assertEqual(
                0,
                result.exit_code,
                'Command did not terminate properly',
            )

            rpc_client.assert_called_with(expected_host, expected_port)

            rpc_client.server_stop_all.assert_called_with()

            success.assert_has_calls(
                [
                    unittest.mock.call('{} successfully stopped'.format(server_id))
                    for server_id in success_ids
                ]
            )

            error.assert_has_calls(
                [
                    unittest.mock.call('{} did not stop properly'.format(server_id))
                    for server_id in error_ids
                ]
            )

if __name__ == '__main__':
    unittest.main()

