"""
Tests for the shutdown command
"""

import unittest
import unittest.mock

from .... import utils

from mymcadmin.cli import mymcadmin as mma_command

class TestShutdown(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the shutdown command
    """

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_default(self, config):
        """
        Tests the the command works properly with the defaults
        """

        config.return_value = config
        config.rpc = None

        self._run_test('localhost', 2323)

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_config(self, config):
        """
        Tests the the command uses the configuration options
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
        Tests the the command uses the command line options
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
        rpc_client.shutdown.side_effect = RuntimeError

        result = self.cli_runner.invoke(mma_command, ['shutdown'])

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

    def _run_test(self, expected_host, expected_port, params = None):
        if params is None:
            params = []

        server_ids = [
            'server0',
            'server1',
            'server2',
        ]

        with unittest.mock.patch('mymcadmin.rpc.RpcClient') as rpc_client, \
             unittest.mock.patch('mymcadmin.cli.commands.shutdown.success') as success:
            rpc_client.return_value = rpc_client
            rpc_client.__enter__.return_value = rpc_client
            rpc_client.shutdown.return_value = server_ids

            result = self.cli_runner.invoke(
                mma_command,
                ['shutdown'] + params,
            )

            if result.exit_code != 0:
                print(result.output)

            self.assertEqual(
                0,
                result.exit_code,
                'The command did not terminate properly',
            )

            rpc_client.assert_called_with(expected_host, expected_port)
            rpc_client.shutdown.assert_called_with()

            success.assert_has_calls(
                [
                    unittest.mock.call('Success'),
                ] + [
                    unittest.mock.call('{} successfully stopped'.format(server_id))
                    for server_id in server_ids
                ]
            )

if __name__ == '__main__':
    unittest.main()

