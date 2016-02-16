"""
Tests for the JSON RPC decorators
"""

import asyncio
import unittest

import nose

from ... import utils

from mymcadmin.rpc.errors import JsonRpcInvalidRequestError
from mymcadmin.rpc.decorators import required_param

class TestRequiredParam(unittest.TestCase):
    """
    Tests for the required_param decorator
    """

    def setUp(self):
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

    def tearDown(self):
        self.event_loop.close()

    @utils.run_async
    async def test_valid(self):
        """
        Tests that the decorator works correctly when given valid input
        """

        @required_param('named_param')
        async def _method(named_param):
            return named_param

        self.assertEqual(
            'this is a test',
            await _method(named_param = 'this is a test'),
            'Method did not function correctly',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(JsonRpcInvalidRequestError)
    @utils.run_async
    async def test_missing(self):
        """
        Tests that an error response is returned if the parameter is missing
        """

        @required_param('named_param')
        async def _method(named_param):
            return named_param

        await _method('this is a test')
    # pylint: enable=no-self-use

if __name__ == '__main__':
    unittest.main()

