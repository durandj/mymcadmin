import click
import click.testing
import unittest
import unittest.mock

from mymcadmin.cli.base import (
	mymcadmin,
	success,
	info,
	warn,
	error,
)

class TestMyMcAdmin(unittest.TestCase):
	def setUp(self):
		self.cli_runner = click.testing.CliRunner()

	def test_main(self):
		result = self.cli_runner.invoke(mymcadmin)

		self.assertEqual(
			0,
			result.exit_code,
			'Did not return success status code',
		)

	def test_config_context(self):
		@mymcadmin.command()
		@click.pass_context
		def test(ctx):
			self.assertIn(
				'config',
				ctx.obj,
			)

		self.cli_runner.invoke(mymcadmin, ['test'])

	@unittest.mock.patch('click.secho')
	def test_success(self, secho):
		success('Hello, world!')
		secho.assert_called_with('Hello, world!', fg = 'green')

	@unittest.mock.patch('click.secho')
	def test_success_formatting(self, secho):
		success('Hello, world!', bold = True)
		secho.assert_called_with('Hello, world!', fg = 'green', bold = True)

	@unittest.mock.patch('click.secho')
	def test_info(self, secho):
		info('Hello, world!')
		secho.assert_called_with('Hello, world!', fg = 'blue')

	@unittest.mock.patch('click.secho')
	def test_info_formatting(self, secho):
		info('Hello, world!', underline = True)
		secho.assert_called_with('Hello, world!', fg = 'blue', underline = True)

	@unittest.mock.patch('click.secho')
	def test_warn(self, secho):
		warn('Hello, world!')
		secho.assert_called_with('Hello, world!', fg = 'yellow')

	@unittest.mock.patch('click.secho')
	def test_warn_formatting(self, secho):
		warn('Hello, world!', strikethrough = True)
		secho.assert_called_with(
			'Hello, world!',
			fg            = 'yellow',
			strikethrough = True,
		)

	@unittest.mock.patch('click.secho')
	def test_error(self, secho):
		error('Hello, world!')
		secho.assert_called_with('Hello, world!', fg = 'red')

	@unittest.mock.patch('click.secho')
	def test_error_formatting(self, secho):
		error('Hello, world!', bg = 'orange')
		secho.assert_called_with('Hello, world!', fg = 'red', bg = 'orange')

if __name__ == '__main__':
	unittest.main()

