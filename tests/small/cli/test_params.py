import click
import getpass
import grp
import nose
import os
import unittest
import unittest.mock

from mymcadmin.cli.params import (
    Server,
    User,
    Group,
)
from mymcadmin.server import Server as ServerInstance

class TestServer(unittest.TestCase):
    def setUp(self):
        self.mock_config = unittest.mock.Mock()
        self.mock_config.configure_mock(instance_path = 'root')

        self.mock_context = unittest.mock.MagicMock()
        self.mock_context.obj = {'config': self.mock_config}

    @unittest.mock.patch('os.path.exists')
    def test_convert_exists(self, exists):
        exists.return_value = True

        param  = Server()
        server = param.convert('i_exist', None, self.mock_context)

        self.assertIsInstance(
            server,
            ServerInstance,
            'Parameter did not return the right type',
        )

        self.assertEqual(
            'root/i_exist',
            server.path,
            'Server was not setup at the right location',
        )

    @nose.tools.raises(click.BadParameter)
    @unittest.mock.patch('os.path.exists')
    def test_convert_exists_fail(self, exists):
        exists.return_value = False

        param = Server()
        param.convert('i_dont_exist', None, self.mock_context)

    @unittest.mock.patch('os.path.exists')
    def test_convert_not_exists(self, exists):
        exists.return_value = False

        param  = Server(exists = False)
        server = param.convert('i_dont_exist', None, self.mock_context)

        self.assertIsInstance(
            server,
            ServerInstance,
            'Parameter did not return the right type',
        )

        self.assertEqual(
            'root/i_dont_exist',
            server.path,
            'Server was not setup at the right location',
        )

class TestUser(unittest.TestCase):
    def test_convert_string(self):
        current_user = getpass.getuser()

        param = User()
        user  = param.convert(current_user, None, None)

        self.assertEqual(
            os.getuid(),
            user,
            'User did not match',
        )

    @nose.tools.raises(click.BadParameter)
    def test_convert_string_fail(self):
        expected_user = 'i_hopefully_dont_exist'

        param = User()
        user  = param.convert(expected_user, None, None)

    def test_convert_int(self):
        expected_uid = os.getuid()

        param = User()
        user  = param.convert(expected_uid, None, None)

        self.assertEqual(
            expected_uid,
            user,
            'User ID did not match',
        )

    @nose.tools.raises(click.BadParameter)
    def test_convert_int_fail(self):
        # This should be way larger than the system limit since its 2^64
        user_id = 0x10000000000000000

        param = User()
        user  = param.convert(user_id, None, None)

class TestGroup(unittest.TestCase):
    def test_convert_string(self):
        expected_gid  = os.getgid()
        current_group = grp.getgrgid(expected_gid).gr_name

        param = Group()
        group = param.convert(current_group, None, None)

        self.assertEqual(
            expected_gid,
            group,
            'Group ID did not match',
        )

    @nose.tools.raises(click.BadParameter)
    def test_convert_string_fail(self):
        param = Group()
        param.convert('i_hopefully_dont_exist', None, None)

    def test_convert_int(self):
        expected_gid = os.getgid()

        param = Group()
        group = param.convert(expected_gid, None, None)

        self.assertEqual(
            expected_gid,
            group,
            'Group ID did not match',
        )

    @nose.tools.raises(click.BadParameter)
    def test_convert_int_fail(self):
        # This should be way larger than the system limit since its 2^64
        group_id = 0x10000000000000000

        param = Group()
        group = param.convert(group_id, None, None)

if __name__ == '__main__':
    unittest.main()

