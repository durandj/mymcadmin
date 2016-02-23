"""
Tests for the server_restart method
"""

import unittest

import asynctest
import nose

from .... import utils

from mymcadmin.errors import ServerDoesNotExistError

class TestServerRestart(utils.ManagerMixin, unittest.TestCase):
    """
    Tests for the server_restart method
    """

    @utils.run_async
    async def test_method(self):
        """
        Tests that the method restarts a server
        """

        server_id = 'testification'

        mock_server_stop  = asynctest.CoroutineMock()
        mock_server_start = asynctest.CoroutineMock()

        self.manager.rpc_command_server_stop  = mock_server_stop
        self.manager.rpc_command_server_start = mock_server_start

        result = await self.manager.rpc_command_server_restart(
            server_id = server_id,
        )

        self.assertEqual(
            server_id,
            result,
            'JSON RPC method did not return the server ID',
        )

        mock_server_stop.assert_called_with(server_id = server_id)
        mock_server_start.assert_called_with(server_id = server_id)

    @nose.tools.raises(ServerDoesNotExistError)
    @utils.run_async
    async def test_method_bad_id(self):
        """
        Tests that we check for a non-existant server ID
        """

        await self.manager.rpc_command_server_restart(
            server_id = 'bad',
        )

    @nose.tools.raises(RuntimeError)
    @utils.run_async
    async def test_method_fail(self):
        """
        Tests that if the restart fails we pass up the error
        """

        mock_server_stop  = asynctest.CoroutineMock()
        mock_server_start = asynctest.CoroutineMock()

        mock_server_stop.side_effect = RuntimeError('Boom!')

        self.manager.rpc_command_server_stop  = mock_server_stop
        self.manager.rpc_command_server_start = mock_server_start

        await self.manager.rpc_command_server_restart(
            server_id = 'testification',
        )

if __name__ == '__main__':
    unittest.main()

