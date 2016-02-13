"""
Tests for the start CLI commands
"""

import os
import unittest
import unittest.mock

import click
import nose

from .... import utils

from mymcadmin.cli import mymcadmin as mma_command
from mymcadmin.cli.commands.start import start_management_daemon, start_server

class TestStart(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the server start command
    """

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command(self, config, exists, server, mock_start_server):
        """
        Test the command with no special options
        """

        config.return_value = config
        config.rpc          = {}

        exists.return_value = True

        server.return_value = server
        server.name         = 'test'

        result = self.cli_runner.invoke(mma_command, ['start', 'test'])

        if result.exit_code != 0:
            print(result.output)

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        mock_start_server.assert_called_with(server, None, None)

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_option_host(self, config, exists, server, mock_start_server):
        """
        Tests that the host option is used
        """

        config.return_value = config
        config.rpc          = {}

        exists.return_value = True

        server.return_value = server
        server.name         = 'test'

        result = self.cli_runner.invoke(
            mma_command,
            [
                'start',
                'test',
                '--host',
                'example.com',
            ]
        )

        if result.exit_code != 0:
            print(result.output)

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        mock_start_server.assert_called_with(server, 'example.com', None)

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_option_port(self, config, exists, server, mock_start_server):
        """
        Tests that the port option is used
        """

        config.return_value = config
        config.rpc          = {}

        exists.return_value = True

        server.return_value = server
        server.name         = 'test'

        result = self.cli_runner.invoke(
            mma_command,
            [
                'start',
                'test',
                '--port',
                2323,
            ]
        )

        if result.exit_code != 0:
            print(result.output)

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        mock_start_server.assert_called_with(server, None, 2323)

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_config_host(self, config, exists, server, mock_start_server):
        """
        Tests that if the host option isn't given it defaults to the config
        """

        config.return_value = config
        config.rpc          = {'host': 'example.com'}

        exists.return_value = True

        server.return_value = server
        server.name         = 'test'

        result = self.cli_runner.invoke(mma_command, ['start', 'test'])

        if result.exit_code != 0:
            print(result.output)

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        mock_start_server.assert_called_with(server, 'example.com', None)

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_config_port(self, config, exists, server, mock_start_server):
        """
        Tests that if the port option isn't given it defaults to the config
        """

        config.return_value = config
        config.rpc          = {'port': 2323}

        exists.return_value = True

        server.return_value = server
        server.name         = 'test'

        result = self.cli_runner.invoke(mma_command, ['start', 'test'])

        if result.exit_code != 0:
            print(result.output)

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        mock_start_server.assert_called_with(server, None, 2323)

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_fail(self, config, exists, server, mock_start_server):
        """
        Test that the command returns a non-zero exit code on error
        """

        config.return_value = config
        config.rpc          = {}

        exists.return_value = True

        server.return_value = server

        mock_start_server.side_effect = click.ClickException('boom')

        result = self.cli_runner.invoke(mma_command, ['start', 'test'])

        if result.exit_code != 1:
            print(result.output)

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

    # pylint: disable=no-self-use
    @unittest.mock.patch('mymcadmin.rpc.RpcClient')
    @unittest.mock.patch('mymcadmin.server.Server')
    def test_start_server(self, server, rpc_client):
        """
        Tests that the start_server function sends the serverStart command
        """

        server.name = 'test'

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client

        start_server(server, None, None)

        rpc_client.assert_called_with('localhost', 2323)
        rpc_client.server_start.assert_called_with('test')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @unittest.mock.patch('mymcadmin.rpc.RpcClient')
    @unittest.mock.patch('mymcadmin.server.Server')
    def test_start_server_host(self, server, rpc_client):
        """
        Tests that the start_server function uses the host option
        """

        server.name = 'test'

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client

        start_server(server, 'example.com', None)

        rpc_client.assert_called_with('example.com', 2323)
        rpc_client.server_start.assert_called_with('test')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @unittest.mock.patch('mymcadmin.rpc.RpcClient')
    @unittest.mock.patch('mymcadmin.server.Server')
    def test_start_server_port(self, server, rpc_client):
        """
        Tests that the start_server function uses the port option
        """

        server.name = 'test'

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client

        start_server(server, None, 8080)

        rpc_client.assert_called_with('localhost', 8080)
        rpc_client.server_start.assert_called_with('test')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(click.ClickException)
    @unittest.mock.patch('mymcadmin.rpc.RpcClient')
    @unittest.mock.patch('mymcadmin.server.Server')
    def test_start_server_fail(self, server, rpc_client):
        """
        Tests that the start_server function handles errors properly
        """

        server.name = 'test'

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client
        rpc_client.server_start.side_effect = RuntimeError

        start_server(server, None, None)
    # pylint: enable=no-self-use

class TestStartAll(utils.CliRunnerMixin, unittest.TestCase):
    """
    start_all tests
    """

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command(self, config, server, exists, mock_start_server):
        """
        Tests that the command works properly with no extra options
        """

        config.return_value = config
        config.rpc          = {}

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

        exists.side_effect = True

        result = self.cli_runner.invoke(mma_command, ['start_all'])

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        mock_start_server.assert_has_calls(
            [
                unittest.mock.call(srv, None, None)
                for srv in servers
            ]
        )

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_host_option(self, config, server, exists, mock_start_server):
        """
        Tests that the host option is used
        """

        config.return_value = config
        config.rpc          = {}

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

        exists.side_effect = True

        result = self.cli_runner.invoke(
            mma_command,
            [
                'start_all',
                '--host',
                'example.com',
            ]
        )

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        mock_start_server.assert_has_calls(
            [
                unittest.mock.call(srv, 'example.com', None)
                for srv in servers
            ]
        )

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_port_option(self, config, server, exists, mock_start_server):
        """
        Tests that the port option is used
        """

        config.return_value = config
        config.rpc          = {}

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

        exists.side_effect = True

        result = self.cli_runner.invoke(
            mma_command,
            [
                'start_all',
                '--port',
                2323
            ]
        )

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        mock_start_server.assert_has_calls(
            [
                unittest.mock.call(srv, None, 2323)
                for srv in servers
            ]
        )

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_host_config(self, config, server, exists, mock_start_server):
        """
        Tests that the host config option is used
        """

        config.return_value = config
        config.rpc          = {'host': 'example.com'}

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

        exists.side_effect = True

        result = self.cli_runner.invoke(mma_command, ['start_all'])

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        mock_start_server.assert_has_calls(
            [
                unittest.mock.call(srv, 'example.com', None)
                for srv in servers
            ]
        )

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_port_config(self, config, server, exists, mock_start_server):
        """
        Tests that the port config option is used
        """

        config.return_value = config
        config.rpc          = {'port': 2323}

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

        exists.side_effect = True

        result = self.cli_runner.invoke(mma_command, ['start_all'])

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        mock_start_server.assert_has_calls(
            [
                unittest.mock.call(srv, None, 2323)
                for srv in servers
            ]
        )

    @unittest.mock.patch('mymcadmin.cli.commands.start.start_server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_fail(self, config, server, exists, mock_start_server):
        """
        Tests that the correct exit code is used if the command fails
        """

        config.return_value = config
        config.rpc          = {}

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

        exists.side_effect = True

        mock_start_server.side_effect = click.ClickException('boom')

        result = self.cli_runner.invoke(mma_command, ['start_all'])

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

class TestStartDaemon(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests the start_daemon command
    """

    @unittest.mock.patch('multiprocessing.Process')
    @unittest.mock.patch('mymcadmin.utils.get_user_home')
    @unittest.mock.patch('mymcadmin.config.Config')
    @unittest.mock.patch('os.path.exists')
    def test_command_default(self, exists, config, get_user_home, process):
        """
        Tests that the command works with no options and no config settings
        """

        root = os.path.join('home', 'mymcadmin')
        pid  = os.path.join(root, 'daemon.pid')
        log  = os.path.join(root, 'mymcadmin.log')

        exists.side_effect = lambda p: p != pid

        config.return_value = config
        config.daemon = None

        get_user_home.return_value = 'home'

        process.return_value = process

        result = self.cli_runner.invoke(mma_command, ['start_daemon'])

        if result.exit_code != 0:
            print(result.output)

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        process.assert_called_with(
            target = start_management_daemon,
            args   = (
                'localhost',
                2323,
                os.getuid(),
                os.getgid(),
                root,
                pid,
                log,
            ),
        )

        process.start.assert_called_with()
        process.join.assert_called_with()

    @unittest.mock.patch('multiprocessing.Process')
    @unittest.mock.patch('mymcadmin.utils.get_user_home')
    @unittest.mock.patch('mymcadmin.config.Config')
    @unittest.mock.patch('os.path.exists')
    def test_command_config(self, exists, config, get_user_home, process):
        """
        Tests that the command works with no options and a full config
        """

        root = os.path.join('home', 'mma')
        pid  = os.path.join(root, 'test.pid')
        log  = os.path.join(root, 'test.log')

        exists.side_effect = lambda p: p != pid

        config.return_value = config
        config.daemon = {
            'host':  'example.com',
            'port':  8080,
            'user':  9999,
            'group': 5555,
            'root':  root,
            'pid':   pid,
            'log':   log,
        }

        get_user_home.return_value = 'home'

        process.return_value = process

        result = self.cli_runner.invoke(mma_command, ['start_daemon'])

        if result.exit_code != 0:
            print(result.output)

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        process.assert_called_with(
            target = start_management_daemon,
            args   = (
                'example.com',
                8080,
                9999,
                5555,
                root,
                pid,
                log,
            ),
        )

        process.start.assert_called_with()
        process.join.assert_called_with()

    # pylint: disable=too-many-arguments
    @unittest.mock.patch('multiprocessing.Process')
    @unittest.mock.patch('mymcadmin.utils.get_user_home')
    @unittest.mock.patch('grp.getgrgid')
    @unittest.mock.patch('pwd.getpwuid')
    @unittest.mock.patch('mymcadmin.config.Config')
    @unittest.mock.patch('os.path.exists')
    def test_command_options(self, exists, config, getpwuid, getgrgid, get_user_home, process):
        """
        Tests that the command uses the given options
        """

        user  = 5000
        group = 5050
        pid   = 'test.pid'

        exists.side_effect = lambda p: p != pid

        config.return_value = config
        config.daemon = None

        getpwuid.return_value = user
        getgrgid.return_value = group

        get_user_home.return_value = 'home'

        process.return_value = process

        result = self.cli_runner.invoke(
            mma_command,
            [
                'start_daemon',
                '--host',  'example.com',
                '--port',  8080,
                '--user',  user,
                '--group', group,
                '--root',  'test',
                '--pid',   pid,
                '--log',   'test.log',
            ]
        )

        if result.exit_code != 0:
            print(result.output)

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        process.assert_called_with(
            target = start_management_daemon,
            args   = (
                'example.com',
                8080,
                user,
                group,
                'test',
                pid,
                'test.log',
            ),
        )

        process.start.assert_called_with()
        process.join.assert_called_with()
    # pylint: enable=too-many-arguments

    @unittest.mock.patch('os.path.exists')
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command_port_invalid(self, exists):
        """
        Test that the command returns an exit code for an invalid port
        """

        exists.return_value = True

        result = self.cli_runner.invoke(
            mma_command,
            [
                'start_daemon',
                '--port', '8000',
            ]
        )

        self.assertEqual(
            -1,
            result.exit_code,
            'Command did not terminate properly',
        )

if __name__ == '__main__':
    unittest.main()

