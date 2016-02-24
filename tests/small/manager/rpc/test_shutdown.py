"""
Tests for the shutdown JSON RPC method
"""

import asyncio
import unittest
import unittest.mock

import asynctest

from .... import utils

class TestShutdown(utils.ManagerMixin, unittest.TestCase):
    """
    Tests for the shutdown JSON RPC method
    """

    @utils.run_async
    async def test_method(self):
        """
        Tests that when shutting down we stop any running instances
        """

        instance_ids = [
            'server0',
            'server1',
            'server2',
            'server3',
        ]

        instances = {
            server_id: asynctest.Mock(spec = asyncio.subprocess.Process)
            for server_id in instance_ids
        }

        self.manager.instances = instances

        mock_server_stop = asynctest.CoroutineMock()
        self.manager.rpc_command_server_stop = mock_server_stop
        self.manager.rpc_command_server_stop.side_effect = instance_ids

        result = await self.manager.rpc_command_shutdown()

        self.assertEqual(
            instance_ids,
            result,
            'Method did not return the correct server IDs',
        )

        mock_server_stop.assert_has_calls(
            [
                unittest.mock.call(server_id = server_id)
                for server_id in instances.keys()
            ]
        )

if __name__ == '__main__':
    unittest.main()

