"""
Tests for the stop_all JSON RPC method
"""

import asyncio
import unittest
import unittest.mock

import asynctest

from .... import utils

class TestServerStopAll(utils.ManagerMixin, unittest.TestCase):
    """
    Tests for the stop_all JSON RPC method
    """

    @utils.run_async
    async def test_method(self):
        """
        Tests that the method works correctly under ideal conditions
        """

        await self._run_test(
            success_ids = ['server0', 'server1', 'server2'],
        )

    @utils.run_async
    async def test_method_server_errors(self):
        """
        Tests that we keep stopping servers even if one or more errors out
        """

        await self._run_test(
            success_ids = ['server0', 'server1', 'server2'],
            error_ids   = ['error0', 'error1'],
        )

    async def _run_test(self, success_ids = None, error_ids = None):
        if success_ids is None:
            success_ids = []

        if error_ids is None:
            error_ids = []

        server_ids = success_ids + error_ids

        server_procs = {
            server_id: asynctest.Mock(spec = asyncio.subprocess.Process)
            for server_id in server_ids
        }

        mock_list_servers = asynctest.CoroutineMock()
        mock_list_servers.return_value = server_ids

        def _stop_func(server_id):
            if server_id not in error_ids:
                return server_id
            else:
                raise RuntimeError('Boom')

        mock_server_stop = asynctest.CoroutineMock()
        mock_server_stop.side_effect = _stop_func

        self.manager.instances = server_procs

        self.manager.rpc_command_list_servers = mock_list_servers
        self.manager.rpc_command_server_stop  = mock_server_stop

        result = await self.manager.rpc_command_server_stop_all()

        mock_server_stop.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in self.manager.instances.keys()
            ]
        )

        self.assertListEqual(
            [
                server_id
                for server_id in self.manager.instances.keys()
                if server_id in success_ids
            ],
            result.get('success'),
            'Method did not return the correct list of successful server IDs',
        )

        self.assertListEqual(
            [
                server_id
                for server_id in self.manager.instances.keys()
                if server_id in error_ids
            ],
            result.get('failure'),
            'Method did not return the correct list of failed server IDs',
        )

if __name__ == '__main__':
    unittest.main()

