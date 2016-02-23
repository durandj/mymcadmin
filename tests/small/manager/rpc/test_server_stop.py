"""
Tests for the server_stop JSON RPC method
"""

import asyncio
import unittest

import asynctest
import nose

from .... import utils

from mymcadmin.errors import ServerDoesNotExistError
from mymcadmin.rpc.errors import JsonRpcInvalidRequestError

class TestServerStop(utils.ManagerMixin, unittest.TestCase):
    """
    Tests for the server_stop JSON RPC method
    """

    @asynctest.patch('mymcadmin.server.Server')
    @asynctest.patch('os.path.exists')
    @utils.run_async
    async def test_method(self, exists, server):
        """
        Tests that the method works properly in ideal conditions
        """

        exists.return_value = True
        server.return_value = server

        server_id = 'testification'
        mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

        self.manager.instances = {
            server_id: mock_proc
        }

        result = await self.manager.rpc_command_server_stop(
            server_id = server_id,
        )

        self.assertEqual(
            server_id,
            result,
            'Method did not return the server ID',
        )

        mock_proc.communicate.assert_called_with('stop'.encode())

    @nose.tools.raises(ServerDoesNotExistError)
    @utils.run_async
    async def test_method_bad_id(self):
        """
        Tests that we check for valid server IDs
        """

        await self.manager.rpc_command_server_stop(
            server_id = 'bad',
        )

    @nose.tools.raises(JsonRpcInvalidRequestError)
    @asynctest.patch('os.path.exists')
    @utils.run_async
    async def test_method_not_running(self, exists):
        """
        Tests that we throw an error when the server isn't running
        """

        exists.return_value = True

        await self.manager.rpc_command_server_stop('testification')

if __name__ == '__main__':
    unittest.main()

