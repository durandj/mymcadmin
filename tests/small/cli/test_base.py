"""
Tests for the base utilities of the CLI
"""

import unittest
import unittest.mock

import click
import click.testing

from mymcadmin.cli.base import (
    mymcadmin,
    rpc_command,
    success,
    info,
    warn,
    error,
)

class TestMyMCAdmin(unittest.TestCase):
    """
    Tests for the main command group
    """

    def setUp(self):
        self.cli_runner = click.testing.CliRunner()

    def test_main(self):
        """
        Tests that the command executes on its own
        """

        result = self.cli_runner.invoke(mymcadmin)

        self.assertEqual(
            0,
            result.exit_code,
            'Did not return success status code',
        )

    def test_config_context(self):
        """
        Tests that the configuration is passed via the context
        """

        # pylint: disable=unused-variable
        @mymcadmin.command()
        @click.pass_context
        def test(ctx):
            """
            Dumby test command
            """

            self.assertIn(
                'config',
                ctx.obj,
            )
        # pylint: enable=unused-variable

        self.cli_runner.invoke(mymcadmin, ['test'])

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_rpc_command_default(self, config):
        """
        Tests that the rpc_command decorator uses sensible defaults
        """

        config.return_value = config
        config.rpc          = None

        self._do_rpc_command('localhost', 2323)

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_rpc_command_config(self, config):
        """
        Tests that the rpc_command decorator uses the config
        """

        config.return_value = config
        config.rpc          = {
            'host': 'example.com',
            'port': 8080,
        }

        self._do_rpc_command('example.com', 8080)

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_rpc_command_options(self, config):
        """
        Tests that the rpc_command decorator uses the CLI options
        """

        config.return_value = config
        config.rpc          = None

        self._do_rpc_command(
            'example.com',
            8080,
            params = [
                '--host', 'example.com',
                '--port', 8080,
            ],
        )

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_rpc_command_cli_first(self, config):
        """
        Tests that the rpc_command decorator uses CLI options over the config
        """

        config.return_value = config
        config.rpc          = {
            'host': 'test.com',
            'port': 8000,
        }

        self._do_rpc_command(
            'example.com',
            8080,
            params = [
                '--host', 'example.com',
                '--port', 8080,
            ],
        )

    def _do_rpc_command(self, expected_host, expected_port, params = None):
        if params is None:
            params = []

        connection = {}

        # pylint: disable=unused-variable
        @mymcadmin.command()
        @rpc_command
        def test(rpc_conn):
            """
            Dumby test command
            """

            connection['host'], connection['port'] = rpc_conn
        # pylint: enable=unused-variable

        result = self.cli_runner.invoke(mymcadmin, ['test'] + params)

        if result.exit_code != 0:
            print(result.output)

        self.assertEqual(
            0,
            result.exit_code,
            'Test command did not terminate properly',
        )

        self.assertDictEqual(
            {'host': expected_host, 'port': expected_port},
            connection,
            'RPC connection details did not match expected',
        )

@unittest.mock.patch('click.secho')
def test_success(secho):
    """
    Tests that the success method works correctly
    """

    success('Hello, world!')
    secho.assert_called_with('Hello, world!', fg = 'green')

@unittest.mock.patch('click.secho')
def test_success_formatting(secho):
    """
    Tests that the success method passes on formatting
    """

    success('Hello, world!', bold = True)
    secho.assert_called_with('Hello, world!', fg = 'green', bold = True)

@unittest.mock.patch('click.secho')
def test_info(secho):
    """
    Tests that the info command works correctly
    """

    info('Hello, world!')
    secho.assert_called_with('Hello, world!', fg = 'blue')

@unittest.mock.patch('click.secho')
def test_info_formatting(secho):
    """
    Tests that the info command passes on formatting
    """

    info('Hello, world!', underline = True)
    secho.assert_called_with('Hello, world!', fg = 'blue', underline = True)

@unittest.mock.patch('click.secho')
def test_warn(secho):
    """
    Tests that the warn command works correctly
    """

    warn('Hello, world!')
    secho.assert_called_with('Hello, world!', fg = 'yellow')

@unittest.mock.patch('click.secho')
def test_warn_formatting(secho):
    """
    Tests that the warn command passes on formatting
    """

    warn('Hello, world!', strikethrough = True)
    secho.assert_called_with(
        'Hello, world!',
        fg            = 'yellow',
        strikethrough = True,
    )

@unittest.mock.patch('click.secho')
def test_error(secho):
    """
    Tests that the error command works correctly
    """

    error('Hello, world!')
    secho.assert_called_with('Hello, world!', fg = 'red')

@unittest.mock.patch('click.secho')
def test_error_formatting(secho):
    """
    Tests that the error command passes on formatting
    """

    error('Hello, world!', bg = 'orange')
    secho.assert_called_with('Hello, world!', fg = 'red', bg = 'orange')

if __name__ == '__main__':
    unittest.main()

