"""
Tests for the JSON RPC interface handling
"""

import asyncio
import unittest

import asynctest

from ... import utils

from mymcadmin.manager import Manager

# pylint: disable=too-many-public-methods
class TestRpcCommands(utils.EventLoopMixin, unittest.TestCase):
    """
    Tests for the JSON RPC commands
    """

    def setUp(self):
        super(TestRpcCommands, self).setUp()

        self.host            = 'example.com'
        self.port            = 8000
        self.root            = 'root'
        self.mock_event_loop = asynctest.Mock(spec = asyncio.BaseEventLoop)

        self.manager = Manager(
            self.host,
            self.port,
            self.root,
            event_loop = self.mock_event_loop,
        )

    @utils.run_async
    async def test_shutdown_running_proc(self):
        """
        Check that the shutdown command stops any running server instances
        """

        instance_ids = ['test0', 'test1', 'test2', 'test3']
        instances    = {}
        for server_id in instance_ids:
            mock = asynctest.Mock(spec = asyncio.subprocess.Process)

            instances[server_id] = mock

        mock_server_stop = asynctest.CoroutineMock()
        self.manager.instances = instances
        self.manager.rpc_command_server_stop = mock_server_stop
        self.manager.rpc_command_server_stop.side_effect = instance_ids

        result = await self.manager.rpc_command_shutdown()

        self.assertEqual(
            instance_ids,
            result,
            'Return message did not match',
        )

        mock_server_stop.assert_has_calls(
            [
                unittest.mock.call(server_id = server_id)
                for server_id in instances.keys()
            ]
        )
# pylint: enable=too-many-public-methods

if __name__ == '__main__':
    unittest.main()

