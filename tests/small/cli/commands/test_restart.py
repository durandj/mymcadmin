"""
Tests for the CLI restart commands
"""

import os.path
import unittest
import unittest.mock

from .... import utils

from mymcadmin.cli import mymcadmin as mma_command

class TestRestart(utils.CliRunnerMixin, unittest.TestCase):
    def setUp(self):
        super(TestRestart, self).setUp()

        self.socket_type = 'tcp'
        self.host        = 'localhost'
        self.port        = 8080

    @unittest.mock.patch('mymcadmin.rpc.RpcClient')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command(self, config, exists, server, rpc_client):
        exists.return_value = True

        server.return_value    = server
        server.name            = 'test'
        server.socket_settings = (self.socket_type, self.host, self.port)

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client

        result = self.cli_runner.invoke(mma_command, ['restart', 'test'])

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate successfully',
        )

        rpc_client.assert_called_with(self.host, self.port)

        self.assertTrue(
            rpc_client.server_restart.called,
            'Server was not restarted',
        )

    @unittest.mock.patch('mymcadmin.rpc.RpcClient')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.path.exists')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command_fail(self, config, exists, server, rpc_client):
        exists.return_value = True

        server.return_value    = server
        server.name            = 'test'
        server.socket_settings = (self.socket_type, self.host, self.port)

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client
        rpc_client.server_restart.side_effect = RuntimeError

        result = self.cli_runner.invoke(mma_command, ['restart', 'test'])

        self.assertEqual(
            1,
            result.exit_code,
            'Command did not terminate successfully',
        )

class TestRestartAll(utils.CliRunnerMixin, unittest.TestCase):
    @unittest.mock.patch('mymcadmin.rpc.RpcClient')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('mymcadmin.config.Config')
    def test_command(self, config, server, rpc_client):
        servers = [
            os.path.join('home', 'test0'),
            os.path.join('home', 'test1'),
            os.path.join('home', 'test2'),
            os.path.join('home', 'test3'),
        ]

        server_connections = [
            ('tcp', 'localhost', 8000),
            ('tcp', 'localhost', 8001),
            ('tcp', 'localhost', 8002),
            ('tcp', 'localhost', 8003),
        ]

        config.return_value = config

        server.list_all.return_value = servers

        mock_socket_settings = unittest.mock.PropertyMock(
            side_effect = server_connections,
        )

        server.return_value = server
        type(server).socket_settings = mock_socket_settings

        rpc_client.return_value = rpc_client
        rpc_client.__enter__.return_value = rpc_client

        result = self.cli_runner.invoke(mma_command, ['restart_all'])

        self.assertEqual(
            0,
            result.exit_code,
            'Command did not terminate properly',
        )

        server.list_all.assert_called_with(config)

        server.assert_has_calls(
            [
                unittest.mock.call(srv)
                for srv in servers
            ]
        )

        for _, host, port in server_connections:
            rpc_client.assert_has_calls([unittest.mock.call(host, port)])

        self.assertEqual(
            len(servers),
            rpc_client.server_restart.call_count,
            'Not all servers were restarted',
        )

if __name__ == '__main__':
    unittest.main()

