"""
Test case mixins
"""

import asyncio

import click.testing

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

