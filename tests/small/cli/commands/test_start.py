"""
Tests for the start CLI commands
"""

import os
import unittest
import unittest.mock

import nose

from .... import utils

from mymcadmin import errors
from mymcadmin.cli import mymcadmin as mma_command
from mymcadmin.cli.commands.start import start_server_daemon

class TestStart(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the server start command
    """

    @unittest.mock.patch('multiprocessing.Process')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command(self, exists, server, process):
        """
        Test the command with no special options
        """

        exists.side_effect = lambda p: p != 'test'

        server.return_value = server
        server.name = 'test'
        server.pid_file = 'test'

        process.return_value = process

        result = self.cli_runner.invoke(mma_command, ['start', 'vanilla'])

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        process.assert_called_with(
            target = start_server_daemon,
            args   = (server, None, None),
        )

        process.start.assert_called_with()
        process.join.assert_called_with()

    @unittest.mock.patch('multiprocessing.Process')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command_fail(self, exists, server, process):
        """
        Tests that the command handles exceptions
        """

        exists.side_effect = lambda p: p != 'test'

        server.return_value = server
        server.name = 'test'
        server.pid_file = 'test'

        process.side_effect = RuntimeError('Boom!')

        result = self.cli_runner.invoke(mma_command, ['start', 'test'])

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

    @unittest.mock.patch('mymcadmin.rpc.RpcClient')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command_manager_started(self, exists, server, rpc_client):
        """
        Tests that the manager is started if it isn't already
        """

        exists.return_value = True

        server.return_value = server
        server.name = 'test'
        server.socket_settings = ('tcp', 'localhost', 8000)

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client

        result = self.cli_runner.invoke(mma_command, ['start', 'test'])

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        rpc_client.server_start.assert_called_with()
        rpc_client.assert_called_with('localhost', 8000)

    @unittest.mock.patch('multiprocessing.Process')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command_user(self, exists, server, process):
        """
        Tests that the user option is used
        """

        exists.side_effect = lambda p: p != 'test'

        server.return_value = server
        server.name = 'test'
        server.pid_file = 'test'

        process.return_value = process

        result = self.cli_runner.invoke(
            mma_command,
            ['start', 'vanilla', '--user', os.getuid()],
        )

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        process.assert_called_with(
            target = start_server_daemon,
            args   = (server, os.getuid(), None),
        )

        process.start.assert_called_with()
        process.join.assert_called_with()

    @unittest.mock.patch('multiprocessing.Process')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command_group(self, exists, server, process):
        """
        Tests that the group option is used
        """

        exists.side_effect = lambda p: p != 'test'

        server.return_value = server
        server.name = 'test'
        server.pid_file = 'test'

        process.return_value = process

        result = self.cli_runner.invoke(
            mma_command,
            ['start', 'vanilla', '--group', os.getgid()],
        )

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        process.assert_called_with(
            target = start_server_daemon,
            args   = (server, None, os.getgid()),
        )

        process.start.assert_called_with()
        process.join.assert_called_with()

    # pylint: disable=no-self-use, too-many-arguments
    @unittest.mock.patch('mymcadmin.manager.Manager')
    @unittest.mock.patch('daemon.pidfile.PIDLockFile')
    @unittest.mock.patch('daemon.DaemonContext')
    @unittest.mock.patch('builtins.open')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.server.Server')
    def test_start_server_daemon(self, server, exists, mock_open, daemon, pidfile, manager):
        """
        Tests that the server daemon is started properly
        """

        server.return_value = server
        server.admin_log = 'test.txt'
        server.pid_file  = 'test.pid'
        server.path      = 'home'

        exists.return_value = False

        mock_open.return_value = mock_open

        pidfile.return_value = pidfile

        manager.return_value = manager

        start_server_daemon(server, None, None)

        mock_open.assert_called_with('test.txt', 'a')

        daemon.assert_called_with(
            detach_process    = True,
            gid               = None,
            pidfile           = pidfile,
            stdout            = open,
            stderr            = open,
            uid               = None,
            working_directory = 'home',
        )

        manager.assert_called_with(server)
        manager.run.assert_called_with()
    # pylint: enable=no-self-use, too-many-arguments

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.MyMCAdminError)
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.server.Server')
    def test_start_server_daemon_fail(self, server, exists):
        """
        Tests that the daemon won't start if it is already started
        """

        exists.return_value = True

        start_server_daemon(server, None, None)
    # pylint: enable=no-self-use

class TestStartAll(utils.CliRunnerMixin, unittest.TestCase):
    """
    start_all tests
    """

    @unittest.mock.patch('multiprocessing.Process')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.server.Server')
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command(self, server, exists, process):
        """
        Tests that the command works properly with no extra options
        """

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
        for srv in servers:
            srv.name     = 'test'
            srv.pid_file = 'test'

        exists.side_effect = lambda p: p != 'test'

        process.return_value = process

        result = self.cli_runner.invoke(mma_command, ['start_all'])

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        for srv in servers:
            process.assert_has_calls(
                [
                    unittest.mock.call(
                        target = start_server_daemon,
                        args   = (srv, None, None),
                    )
                ]
            )

        self.assertEqual(
            len(servers),
            process.start.call_count,
            'Not all servers were started',
        )

        self.assertEqual(
            len(servers),
            process.join.call_count,
        )

    @unittest.mock.patch('multiprocessing.Process')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.server.Server')
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command_user(self, server, exists, process):
        """
        Tests that the user option is used
        """

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
        for srv in servers:
            srv.name     = 'test'
            srv.pid_file = 'test'

        exists.side_effect = lambda p: p != 'test'

        process.return_value = process

        result = self.cli_runner.invoke(
            mma_command,
            ['start_all', '--user', os.getuid()],
        )

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        for srv in servers:
            process.assert_has_calls(
                [
                    unittest.mock.call(
                        target = start_server_daemon,
                        args   = (srv, os.getuid(), None),
                    )
                ]
            )

        self.assertEqual(
            len(servers),
            process.start.call_count,
            'Not all servers were started',
        )

        self.assertEqual(
            len(servers),
            process.join.call_count,
        )

    @unittest.mock.patch('multiprocessing.Process')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.server.Server')
    @utils.apply_mock('mymcadmin.config.Config')
    def test_command_group(self, server, exists, process):
        """
        Tests that the group option is used
        """

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
        for srv in servers:
            srv.name     = 'test'
            srv.pid_file = 'test'

        exists.side_effect = lambda p: p != 'test'

        process.return_value = process

        result = self.cli_runner.invoke(
            mma_command,
            ['start_all', '--group', os.getgid()],
        )

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        for srv in servers:
            process.assert_has_calls(
                [
                    unittest.mock.call(
                        target = start_server_daemon,
                        args   = (srv, None, os.getgid()),
                    )
                ]
            )

        self.assertEqual(
            len(servers),
            process.start.call_count,
            'Not all servers were started',
        )

        self.assertEqual(
            len(servers),
            process.join.call_count,
        )

if __name__ == '__main__':
    unittest.main()

