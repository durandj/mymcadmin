"""
Tests for the system config system
"""

import io
import json
import os.path
import unittest
import unittest.mock

import nose

from mymcadmin import errors
from mymcadmin.config import Config

class TestConfig(unittest.TestCase):
    """
    Tests for the Config class
    """

    def setUp(self):
        self.user_home = os.path.expanduser('~')

    @unittest.mock.patch('builtins.open')
    def test_constructor_default(self, mock_open):
        """
        Tests that the constructor uses a suitable default value
        """

        mock_open.return_value = io.StringIO(
            json.dumps(
                {
                    'test': 'value',
                }
            )
        )

        Config()

        mock_open.assert_called_with(
            os.path.join(self.user_home, '.mymcadminrc'),
            'r',
        )

    # pylint: disable=no-self-use
    @unittest.mock.patch('builtins.open')
    def test_constructor(self, mock_open):
        """
        Tests that the constructor respects the given path
        """

        mock_open.return_value = io.StringIO(
            json.dumps(
                {
                    'test': 'value',
                }
            )
        )

        Config(config_file = 'test.txt')

        mock_open.assert_called_with(
            'test.txt',
            'r',
        )
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.ConfigurationError)
    @unittest.mock.patch('builtins.open')
    def test_constructor_error_open(self, mock_open):
        """
        Tests that we handle when there's an error opening a file
        """

        mock_open.side_effect = FileNotFoundError('Oh, no!')

        Config()
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.ConfigurationError)
    @unittest.mock.patch('builtins.open')
    def test_constructor_error_json(self, mock_open):
        """
        Tests that we handle when the file contains bad JSON
        """

        mock_open.return_value = '['

        Config()
    # pylint: enable=no-self-use

    @unittest.mock.patch('builtins.open')
    def test_getattr(self, mock_open):
        """
        Tests that we can retrieve any value by name
        """

        mock_open.return_value = io.StringIO(
            json.dumps(
                {
                    'test': 'value',
                }
            )
        )

        config = Config()

        self.assertEqual(
            config.test,
            'value',
            'Unable to retrieve configuration value',
        )

    @unittest.mock.patch('builtins.open')
    def test_getattr_missing(self, mock_open):
        """
        Tests that we handle a configuration error
        """

        mock_open.return_value = io.StringIO(
            json.dumps(
                {
                    'test': 'value',
                }
            )
        )

        config = Config()

        self.assertIsNone(
            config.missing,
            'Default config value is not None',
        )

if __name__ == '__main__':
    unittest.main()

