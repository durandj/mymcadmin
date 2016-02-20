"""
Tests the methods of the Server class
"""

import asyncio
import os.path
import unittest
import unittest.mock

import asynctest

from ... import utils

from mymcadmin.server import Server

class TestServerMethods(unittest.TestCase):
    """
    Tests the methods of the Server class
    """

    def setUp(self):
        self.server_id   = 'test_server'
        self.server_path = os.path.join('test', self.server_id)

        self.server = Server(self.server_path)

    @asynctest.patch('asyncio.create_subprocess_exec')
    def test_start(self, create_subprocess_exec):
        """
        Tests the server start command works as expected
        """

        create_subprocess_exec.return_value = create_subprocess_exec

        with utils.mock_property(self.server, 'command_args') as command_args:
            command_args.return_value = [
                'java',
                '-jar',
                'minecraft_server.jar',
            ]

            self.server.start()

            create_subprocess_exec.assert_called_with(
                'java',
                '-jar',
                'minecraft_server.jar',
                cwd    = self.server_path,
                stdin  = asyncio.subprocess.PIPE,
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE,
            )

if __name__ == '__main__':
    unittest.main()

