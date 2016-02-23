"""
Tests for the server_start JSON RPC method
"""

import unittest

import asynctest
import nose

from .... import utils

from mymcadmin.errors import ServerDoesNotExistError

class TestServerStart(utils.ManagerMixin, unittest.TestCase):
    """
    Tests for the server_start JSON RPC method
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

        mock_start_server_proc = asynctest.CoroutineMock()
        self.manager.start_server_proc = mock_start_server_proc

        result = await self.manager.rpc_command_server_start(
            server_id = server_id,
        )

        self.assertEqual(
            server_id,
            result,
            'Method did not return the correct server ID',
        )

        mock_start_server_proc.assert_called_with(server)

    @nose.tools.raises(ServerDoesNotExistError)
    @utils.run_async
    async def test_method_bad_id(self):
        """
        Tests that we check for a valid server_id
        """

        await self.manager.rpc_command_server_start(
            server_id = 'bad',
        )

if __name__ == '__main__':
    unittest.main()

