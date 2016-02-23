"""
Test case mixins
"""

import asyncio

import click.testing
import asynctest

from mymcadmin import manager

# pylint: disable=invalid-name, too-few-public-methods
class CliRunnerMixin(object):
    """
    TestCase mixin for adding CLI runner to the test environment
    """

    def setUp(self):
        """
        Setup the test CLI runner
        """

        self.cli_runner = click.testing.CliRunner()
# pylint: enable=invalid-name, too-few-public-methods

# pylint: disable=invalid-name
class EventLoopMixin(object):
    """
    TestCase mixin that adds a managed event loop to the test environment
    """

    def setUp(self):
        """
        Set up the event loop
        """

        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

    def tearDown(self):
        """
        Shutdown the event loop
        """

        self.event_loop.close()
# pylint: enable=invalid-name

class ManagerMixin(EventLoopMixin):
    """
    TestCase mixin that adds a manager instance to the test environment
    """

    def setUp(self):
        super(ManagerMixin, self).setUp()

        self.root            = 'root'
        self.mock_event_loop = asynctest.Mock(spec = asyncio.BaseEventLoop)
        self.manager         = manager.Manager(
            'localhost',
            2323,
            self.root,
            event_loop = self.mock_event_loop,
        )

