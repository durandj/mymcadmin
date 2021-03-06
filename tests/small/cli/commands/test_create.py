"""
Tests for CLI create commands
"""

import unittest

from .... import utils

from mymcadmin.cli.base import mymcadmin as mma_command

class TestCreate(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the create CLI command
    """

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_default(self, config):
        """
        Tests that the command uses sensible defaults
        """

        config.return_value = config
        config.rpc          = None

        self._run_test(
            'localhost',
            2323,
        )

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_config(self, config):
        """
        Tests that the command uses the config
        """

        config.return_value = config
        config.rpc          = {
            'host': 'example.com',
            'port': 8080,
        }

        self._run_test(
            'example.com',
            8080,
        )

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_options(self, config):
        """
        Tests that the command uses the CLI options
        """

        config.return_value = config
        config.rpc          = None

        self._run_test(
            'example.com',
            8080,
            expected_forge = '10.10.10.10',
            params         = [
                '--forge',
                '--forge_version', '10.10.10.10',
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
        config.rpc          = None

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client
        rpc_client.create.side_effect = RuntimeError('Boom!')

        result = self.cli_runner.invoke(mma_command, ['create', 'test'])

        if result.exit_code != 1:
            print(result.output)

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

    def _run_test(self, expected_host, expected_port,
                  expected_version = None, expected_forge = None, params = None):
        if params is None:
            params = []

        server_id = 'testification'

        with unittest.mock.patch('mymcadmin.rpc.RpcClient') as rpc_client, \
             unittest.mock.patch('mymcadmin.cli.commands.create.warn') as warn, \
             unittest.mock.patch('click.confirm') as confirm, \
             unittest.mock.patch('mymcadmin.cli.commands.create.success') as success:
            rpc_client.return_value = rpc_client
            rpc_client.__enter__.return_value = rpc_client
            rpc_client.server_create.return_value = expected_version or '1.8.9'

            result = self.cli_runner.invoke(
                mma_command,
                [
                    'create',
                    server_id,
                ] + params,
            )

            if result.exit_code != 0:
                print(result.output)

            self.assertEqual(
                0,
                result.exit_code,
                'Command did not terminate properly',
            )

            warn.assert_has_calls(
                [
                    unittest.mock.call(
                        'By creating a server you are agreeing to Mojang\'s EULA.',
                    ),
                    unittest.mock.call(
                        'https://account.mojang.com/documents/minecraft_eula',
                        underline = True,
                    ),
                ]
            )

            confirm.assert_called_with(
                'Do you agree to the EULA?',
                abort = True,
            )

            expected_kwargs = {}
            if expected_forge:
                expected_kwargs['forge'] = expected_forge

            rpc_client.assert_called_with(expected_host, expected_port)
            rpc_client.server_create.assert_called_with(
                server_id,
                expected_version,
                **expected_kwargs
            )

            success.assert_called_with(
                'Server {} successfully created'.format(server_id),
            )

if __name__ == '__main__':
    unittest.main()

