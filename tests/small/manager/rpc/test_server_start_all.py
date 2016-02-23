"""
Tests for the server_start_all JSON RPC method
"""

import asyncio
import unittest
import unittest.mock

import asynctest

from .... import utils

class TestServerStartAll(utils.ManagerMixin, unittest.TestCase):
    """
    Tests for the server_start_all JSON RPC method
    """

    @utils.run_async
    async def test_method(self):
        """
        Tests that the method works correctly in ideal conditions
        """

        await self._run_test(
            success_ids = ['server0', 'server1', 'server2'],
        )

    @utils.run_async
    async def test_method_servers_started(self):
        """
        Tests that we don't try and start servers that are already running
        """

        await self._run_test(
            success_ids = ['server0', 'server1', 'server2'],
            running_ids = ['running0', 'running1'],
        )

    @utils.run_async
    async def test_method_server_errors(self):
        """
        Tests that we keep starting servers even if one or more errors out
        """

        await self._run_test(
            success_ids = ['server0', 'server1', 'server2'],
            error_ids   = ['error0', 'error1', 'error2', 'error3'],
        )

    async def _run_test(self, success_ids = None, error_ids = None, running_ids = None):
        if success_ids is None:
            success_ids = []

        if error_ids is None:
            error_ids = []

        if running_ids is None:
            running_ids = []

        server_ids = success_ids + error_ids + running_ids

        mock_list_servers = asynctest.CoroutineMock()
        mock_list_servers.return_value = server_ids

        def _start_func(server_id):
            if server_id not in error_ids:
                return server_id
            else:
                raise RuntimeError('Boom!')

        mock_server_start = asynctest.CoroutineMock()
        mock_server_start.side_effect = _start_func

        self.manager.rpc_command_list_servers = mock_list_servers
        self.manager.rpc_command_server_start = mock_server_start

        self.manager.instances = {
            server_id: asynctest.Mock(spec = asyncio.subprocess.Process)
            for server_id  in running_ids
        }

        result = await self.manager.rpc_command_server_start_all()

        mock_server_start.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in success_ids
            ]
        )

        self.assertListEqual(
            success_ids,
            result.get('success'),
            'The list of successful servers did not match the expected',
        )

        self.assertListEqual(
            error_ids,
            result.get('failure'),
            'The list of failed servers did not match the expected',
        )

if __name__ == '__main__':
    unittest.main()

