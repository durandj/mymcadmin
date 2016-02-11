"""
Tests for the CLI stop commands
"""

import unittest
import unittest.mock

from .... import utils

from mymcadmin.cli import mymcadmin as mma_command

class TestStop(utils.CliRunnerMixin, unittest.TestCase):
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command(self, config, exists, server):
        exists.return_value = True

        server.return_value = server
        server.name         = 'test'

        result = self.cli_runner.invoke(mma_command, ['stop', 'test'])

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        server.stop.assert_called_with()

    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_fail(self, config, exists, server):
        exists.return_value = True

        server.return_value = server
        server.name         = 'test'
        server.stop.side_effect = RuntimeError

        result = self.cli_runner.invoke(mma_command, ['stop', 'test'])

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

class TestStopAll(utils.CliRunnerMixin, unittest.TestCase):
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command(self, config, server):
        server_names = [
            'test0',
            'test1',
            'test2',
            'test3',
        ]

        servers = [
            unittest.mock.Mock(),
            unittest.mock.Mock(),
            unittest.mock.Mock(),
            unittest.mock.Mock(),
        ]

        server.list_all.return_value = server_names
        server.side_effect = servers

        result = self.cli_runner.invoke(mma_command, ['stop_all'])

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        for srv in servers:
            srv.stop.assert_called_with()

    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_fail(self, config, server):
        server_names = [
            'test0',
            'test1',
            'test2',
            'test3',
        ]

        servers = [
            unittest.mock.Mock(),
            unittest.mock.Mock(),
            unittest.mock.Mock(),
            unittest.mock.Mock(),
        ]

        server.list_all.return_value = server_names
        server.side_effect = servers

        servers[0].stop.side_effect = RuntimeError

        result = self.cli_runner.invoke(mma_command, ['stop_all'])

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate properly',
        )

if __name__ == '__main__':
    unittest.main()

