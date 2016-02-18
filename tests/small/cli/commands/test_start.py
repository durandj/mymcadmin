"""
Tests for the start CLI commands
"""

import os
import unittest
import unittest.mock

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
            'error2',
        ]

        with unittest.mock.patch('mymcadmin.rpc.RpcClient') as rpc_client, \
             unittest.mock.patch('mymcadmin.cli.commands.start.success') as success, \
             unittest.mock.patch('mymcadmin.cli.commands.start.error') as error:
            rpc_client.return_value = rpc_client
            rpc_client.__enter__.return_value = rpc_client
            rpc_client.server_start_all.return_value = {
                'success': success_ids,
                'failure': error_ids,
            }

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
                    for server_id in success_ids
                ]
            )

            error.assert_has_calls(
                [
                    unittest.mock.call('{} did not start properly'.format(server_id))
                    for server_id in error_ids
                ]
            )

class TestStartDaemon(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests the start_daemon command
    """

    def test_command_default(self):
        """
        Tests that the command works with no options and no config settings
        """

        root = os.path.join('home', 'mymcadmin')
        pid  = os.path.join(root, 'daemon.pid')
        log  = os.path.join(root, 'mymcadmin.log')

        self._run_test(
            host  = 'localhost',
            port  = 2323,
            user  = os.getuid(),
            group = os.getgid(),
            root  = root,
            pid   = pid,
            log   = log,
        )

    def test_command_config(self):
        """
        Tests that the command works with no options and a full config
        """

        root = os.path.join('home', 'mma')
        pid  = os.path.join(root, 'test.pid')
        log  = os.path.join(root, 'test.log')

        self._run_test(
            host   = 'example.com',
            port   = 8080,
            user   = 9999,
            group  = 5555,
            root   = root,
            pid    = pid,
            log    = log,
            daemon = {
                'host':  'example.com',
                'port':  8080,
                'user':  9999,
                'group': 5555,
                'root':  root,
                'pid':   pid,
                'log':   log,
            },
        )

    def test_command_config_convert(self):
        """
        Tests that usernames and group names are converted to UIDs and GIDs
        """

        root = os.path.join('home', 'mymcadmin')
        pid  = os.path.join(root, 'daemon.pid')
        log  = os.path.join(root, 'mymcadmin.log')

        self._run_test(
            host   = 'localhost',
            port   = 2323,
            user   = 9999,
            group  = 5555,
            root   = root,
            pid    = pid,
            log    = log,
            daemon = {
                'user':  'im_a_user',
                'group': 'im_a_group',
            },
        )

    def test_command_options(self):
        """
        Tests that the command uses the given options
        """

        self._run_test(
            host  = 'example.com',
            port  = 8080,
            user  = 5000,
            group = 5050,
            root  = 'test',
            pid   = 'test.pid',
            log   = 'test.log',
            params = [
                '--host',  'example.com',
                '--port',  8080,
                '--user',  5000,
                '--group', 5050,
                '--root',  'test',
                '--pid',   'test.pid',
                '--log',   'test.log',
            ],
        )

    @unittest.mock.patch('mymcadmin.config.Config')
    @utils.apply_mock('multiprocessing.Process')
    def test_command_port_invalid(self, config):
        """
        Test that the command returns an exit code for an invalid port
        """

        config.return_value = config
        config.daemon       = None

        result = self.cli_runner.invoke(
            mma_command,
            [
                'start_daemon',
                '--port', '"8000"',
            ]
        )

        if result.exit_code != -1:
            print(result.output)

        self.assertEqual(
            2,
            result.exit_code,
            'Command did not terminate properly',
        )

    @unittest.mock.patch('mymcadmin.config.Config')
    @utils.apply_mock('multiprocessing.Process')
    def test_command_user_invalid_str(self, config):
        """
        Tests that the command returns an exit code for a non-existant user
        """

        config.return_value = config
        config.daemon       = {
            'user': 'i_hopefully_dont_exist',
        }

        result = self.cli_runner.invoke(mma_command, ['start_daemon'])

        if result.exit_code != 1:
            print(result.output)

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

    @unittest.mock.patch('mymcadmin.config.Config')
    @utils.apply_mock('multiprocessing.Process')
    def test_command_user_invalid_int(self, config):
        """
        Tests that the command returns an exit code for a non-existant UID
        """

        config.return_value = config
        config.daemon       = {
            'user': 0x100000000,
        }

        result = self.cli_runner.invoke(mma_command, ['start_daemon'])

        if result.exit_code != 1:
            print(result.output)

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

    @unittest.mock.patch('mymcadmin.config.Config')
    @utils.apply_mock('multiprocessing.Process')
    def test_command_group_invalid_str(self, config):
        """
        Tests that the command returns an exit code for a non-existant group
        """

        config.return_value = config
        config.daemon       = {
            'group': 'i_hopefully_dont_exist',
        }

        result = self.cli_runner.invoke(mma_command, ['start_daemon'])

        if result.exit_code != 1:
            print(result.output)

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

    @unittest.mock.patch('mymcadmin.config.Config')
    @utils.apply_mock('multiprocessing.Process')
    def test_command_group_invalid_int(self, config):
        """
        Tests that the command returns an exit code for a non-existant group
        """

        config.return_value = config
        config.daemon       = {
            'group': 0x1000000000,
        }

        result = self.cli_runner.invoke(mma_command, ['start_daemon'])

        if result.exit_code != 1:
            print(result.output)

        self.assertEqual(
            1,
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

    def _run_test(self, **kwargs):
        host   = kwargs.get('host')
        port   = kwargs.get('port')
        user   = kwargs.get('user')
        group  = kwargs.get('group')
        root   = kwargs.get('root')
        pid    = kwargs.get('pid')
        log    = kwargs.get('log')
        daemon = kwargs.get('daemon')
        params = kwargs.get('params', [])

        with unittest.mock.patch('os.path.exists') as exists, \
             unittest.mock.patch('mymcadmin.config.Config') as config, \
             unittest.mock.patch('pwd.getpwuid') as getpwuid, \
             unittest.mock.patch('pwd.getpwnam') as getpwnam, \
             unittest.mock.patch('grp.getgrgid') as getgrgid, \
             unittest.mock.patch('grp.getgrnam') as getgrnam, \
             unittest.mock.patch('mymcadmin.utils.get_user_home') as get_user_home, \
             unittest.mock.patch('multiprocessing.Process') as process:
            exists.side_effect = lambda p: p != pid

            config.return_value = config
            config.daemon       = daemon

            get_user_home.return_value = 'home'

            if user is not None:
                getpwuid.return_value = user

                getpwnam.return_value = getpwnam
                getpwnam.pw_uid = user

            if group is not None:
                getgrgid.return_value = group

                getgrnam.return_value = getgrnam
                getgrnam.gr_gid = group

            process.return_value = process

            result = self.cli_runner.invoke(
                mma_command,
                ['start_daemon'] + params,
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
                kwargs = {
                    'host':  host,
                    'port':  port,
                    'user':  user,
                    'group': group,
                    'root':  root,
                    'pid':   pid,
                    'log':   log,
                },
            )

            process.start.assert_called_with()
            process.join.assert_called_with()

if __name__ == '__main__':
    unittest.main()

