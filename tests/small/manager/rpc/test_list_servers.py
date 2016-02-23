"""
Tests for the list_servers JSON RPC method
"""

import os.path
import unittest

import asynctest

from .... import utils

class TestListServers(utils.ManagerMixin, unittest.TestCase):
    """
    Tests for the list_servers JSON RPC method
    """

    @asynctest.patch('os.path.isdir')
    @asynctest.patch('os.listdir')
    @utils.run_async
    async def test_method(self, listdir, isdir):
        """
        Tests that the method runs properly
        """

        listdir.return_value = [
            'server0',
            'server1',
            'server2',
            'settings.file',
        ]

        dir_path = os.path.join(self.root, 'server')

        isdir.side_effect = lambda p: p.startswith(dir_path)

        result = await self.manager.rpc_command_list_servers()

        self.assertListEqual(
            ['server0', 'server1', 'server2'],
            result,
            'The server list did not match the expected',
        )

if __name__ == '__main__':
    unittest.main()

