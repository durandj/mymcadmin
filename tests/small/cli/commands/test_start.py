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
from mymcadmin.cli.commands.start import start_management_daemon

class TestStart(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the server start command
    """

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_default(self, config):
        """
        Test the command with no special options
        """

        config.return_value = config
        config.rpc          = None

        self._run_test('localhost', 2323)

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_config(self, config):
        """
        Tests that the command uses the configuration options
        """

        config.return_value = config
        config.rpc          = {
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
        config.rpc          = None

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
        Test that the command returns a non-zero exit code on error
        """

        config.return_value = config
        config.rpc          = {}

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client
        rpc_client.server_start.side_effect = RuntimeError('Boom!')

        result = self.cli_runner.invoke(mma_command, ['start', 'test'])

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

        with unittest.mock.patch('mymcadmin.rpc.RpcClient') as rpc_client:
            rpc_client.return_value = rpc_client
            rpc_client.__enter__.return_value = rpc_client

            result = self.cli_runner.invoke(
                mma_command,
                ['start', 'test'] + params,
            )

            if result.exit_code != 0:
                print(result.output)

            self.assertEqual(
                0,
                result.exit_code,
                'Command did not terminate properly',
            )

            rpc_client.assert_called_with(expected_host, expected_port)

            rpc_client.server_start.assert_called_with('test')

class TestStartAll(utils.CliRunnerMixin, unittest.TestCase):
    """
    start_all tests
    """

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_default(self, config):
        """
        Tests that the command works properly with no extra options
        """

        config.return_value = config
        config.rpc          = None

        self._run_test('localhost', 2323)

    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_config(self, config):
        """
        Tests that the command uses the configuration options
        """

        config.return_value = config
        config.rpc          = {
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
        config.rpc          = None

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
        Tests that the correct exit code is used if the command fails
        """

        config.return_value = config
        config.rpc          = None

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client
        rpc_client.server_start_all.side_effect = RuntimeError('Boom!')

        result = self.cli_runner.invoke(mma_command, ['start_all'])

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
            'server3',
            'server4',
        ]

        with unittest.mock.patch('mymcadmin.rpc.RpcClient') as rpc_client, \
                unittest.mock.patch('mymcadmin.cli.commands.start.success') as success:
            rpc_client.return_value = rpc_client
            rpc_client.__enter__.return_value = rpc_client
            rpc_client.server_start_all.return_value = server_ids

            result = self.cli_runner.invoke(
                mma_command,
                ['start_all'] + params,
            )

            if result.exit_code != 0:
                print(result.output)

            self.assertEqual(
                0,
                result.exit_code,
                'Command did not terminate properly',
            )

            rpc_client.assert_called_with(expected_host, expected_port)

            rpc_client.server_start_all.assert_called_with()

            success.assert_has_calls(
                [
                    unittest.mock.call('{} successfully started'.format(server_id))
                    for server_id in server_ids
                ]
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

    # pylint: disable=no-self-use
    @unittest.mock.patch('mymcadmin.manager.Manager')
    @unittest.mock.patch('daemon.pidfile.PIDLockFile')
    @unittest.mock.patch('daemon.DaemonContext')
    @unittest.mock.patch('builtins.open')
    def test_start_management_daemon(self, mock_open, daemon, pidlockfile, manager):
        """
        Tests that the daemon process is started properly
        """

        mock_open.return_value = mock_open

        daemon.return_value = daemon

        pidlockfile.return_value = pidlockfile

        manager.return_value = manager

        start_management_daemon(
            host  = 'example.com',
            port  = 8080,
            user  = 5050,
            group = 5000,
            root  = 'home',
            pid   = 'daemon.pid',
            log   = 'mymcadmin.log',
        )

        mock_open.assert_called_with('mymcadmin.log', 'a')

        daemon.assert_called_with(
            detach_process    = True,
            gid               = 5000,
            pidfile           = pidlockfile,
            stdout            = mock_open,
            stderr            = mock_open,
            uid               = 5050,
            working_directory = 'home',
        )

        manager.assert_called_with('example.com', 8080, 'home')
        manager.run.assert_called_with()

        mock_open.close.assert_called_with()
    # pylint: enable=no-self-use

if __name__ == '__main__':
    unittest.main()

