"""
Tests for the base utilities of the CLI
"""

import unittest
import unittest.mock

import click
import click.testing

from mymcadmin.cli.base import (
    mymcadmin,
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

    # pylint: disable=no-self-use
    @unittest.mock.patch('click.secho')
    def test_success(self, secho):
        """
        Tests that the success method works correctly
        """

        success('Hello, world!')
        secho.assert_called_with('Hello, world!', fg = 'green')

    @unittest.mock.patch('click.secho')
    def test_success_formatting(self, secho):
        """
        Tests that the success method passes on formatting
        """

        success('Hello, world!', bold = True)
        secho.assert_called_with('Hello, world!', fg = 'green', bold = True)

    @unittest.mock.patch('click.secho')
    def test_info(self, secho):
        """
        Tests that the info command works correctly
        """

        info('Hello, world!')
        secho.assert_called_with('Hello, world!', fg = 'blue')

    @unittest.mock.patch('click.secho')
    def test_info_formatting(self, secho):
        """
        Tests that the info command passes on formatting
        """

        info('Hello, world!', underline = True)
        secho.assert_called_with('Hello, world!', fg = 'blue', underline = True)

    @unittest.mock.patch('click.secho')
    def test_warn(self, secho):
        """
        Tests that the warn command works correctly
        """

        warn('Hello, world!')
        secho.assert_called_with('Hello, world!', fg = 'yellow')

    @unittest.mock.patch('click.secho')
    def test_warn_formatting(self, secho):
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
    def test_error(self, secho):
        """
        Tests that the error command works correctly
        """

        error('Hello, world!')
        secho.assert_called_with('Hello, world!', fg = 'red')

    @unittest.mock.patch('click.secho')
    def test_error_formatting(self, secho):
        """
        Tests that the error command passes on formatting
        """

        error('Hello, world!', bg = 'orange')
        secho.assert_called_with('Hello, world!', fg = 'red', bg = 'orange')
    # pylint: enable=no-self-use

if __name__ == '__main__':
    unittest.main()

