"""
Tests for the JSON RPC restart_all method
"""

import unittest
import unittest.mock

import asynctest

from .... import utils

from mymcadmin.server import Server

class TestRestartAll(utils.ManagerMixin, unittest.TestCase):
    """
    Tests for the JSON RPC restart_all method
    """

    @utils.run_async
    async def test_method(self):
        """
        Tests that the method works properly in ideal conditions
        """

        server_ids = [
            'server0',
            'server1',
            'server2',
        ]

        mock_server_restart = asynctest.CoroutineMock()
        mock_server_restart.side_effect = server_ids

        self.manager.instances = {
            server_id: asynctest.Mock(spec = Server)
            for server_id in server_ids
        }

        self.manager.rpc_command_server_restart = mock_server_restart

        result = await self.manager.rpc_command_server_restart_all()

        mock_server_restart.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in self.manager.instances.keys()
            ]
        )

        self.assertListEqual(
            server_ids,
            result.get('success'),
            'Did not return the correct list of server IDs',
        )

        self.assertListEqual(
            [],
            result.get('failure'),
            'Did not return the correct list of server IDs',
        )

    @utils.run_async
    async def test_method_errors(self):
        """
        Tests that we keep going if one server errors out
        """

        success_ids = ['success0', 'success1', 'success2']
        error_ids   = ['error0', 'error1', 'error2']

        server_ids = success_ids + error_ids

        self.manager.instances = {
            server_id: asynctest.Mock(spec = Server)
            for server_id in server_ids
        }

        def _restart_func(server_id):
            if server_id.startswith('success'):
                return server_id
            else:
                raise RuntimeError('Boom')

        mock_server_restart = asynctest.CoroutineMock()
        mock_server_restart.side_effect = _restart_func

        self.manager.rpc_command_server_restart = mock_server_restart

        result = await self.manager.rpc_command_server_restart_all()

        self.assertListEqual(
            [
                server_id
                for server_id in self.manager.instances.keys()
                if server_id.startswith('success')
            ],
            result.get('success'),
            'The list of restarted servers did not match the expected',
        )

        self.assertListEqual(
            [
                server_id
                for server_id in self.manager.instances.keys()
                if not server_id.startswith('success')
            ],
            result.get('failure'),
            'The list of failures did not match the expected',
        )

if __name__ == '__main__':
    unittest.main()

