import io
import json
import nose
import os.path
import unittest
import unittest.mock

from mymcadmin import errors
from mymcadmin.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.user_home = os.path.expanduser('~')

    @unittest.mock.patch('builtins.open')
    def test_constructor_default(self, open):
        open.return_value = io.StringIO(
            json.dumps(
                {
                    'test': 'value',
                }
            )
        )

        config = Config()

        open.assert_called_with(
            os.path.join(self.user_home, '.mymcadminrc'),
            'r',
        )

    @unittest.mock.patch('builtins.open')
    def test_constructor(self, open):
        open.return_value = io.StringIO(
            json.dumps(
                {
                    'test': 'value',
                }
            )
        )

        config = Config(config_file = 'test.txt')

        open.assert_called_with(
            'test.txt',
            'r',
        )

    @unittest.mock.patch('builtins.open')
    def test_getattr(self, open):
        open.return_value = io.StringIO(
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

    @nose.tools.raises(errors.ConfigurationError)
    @unittest.mock.patch('builtins.open')
    def test_getattr_error(self, open):
        open.return_value = io.StringIO(
            json.dumps(
                {
                    'test': 'value',
                }
            )
        )

        config = Config()

        config.broked

if __name__ == '__main__':
    unittest.main()

