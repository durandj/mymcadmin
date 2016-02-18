"""
Tests for CLI create commands
"""

import unittest

from .... import utils

class TestCreateServer(utils.CliRunnerMixin, unittest.TestCase):
    """
    Tests for the create_server CLI command
    """

    def test_command_default(self):
        """
        Tests that the command uses sensible defaults
        """

        self.fail()

    def test_command_fail(self):
        """
        Tests that the command handles exceptions
        """

        self.fail()

if __name__ == '__main__':
    unittest.main()

