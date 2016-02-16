"""
Tests for the custom CLI parameter types
"""

import getpass
import grp
import os
import unittest
import unittest.mock

import click
import nose

from mymcadmin.cli.params import (
    User,
    Group,
)

class TestUser(unittest.TestCase):
    """
    Tests for the User parameter type
    """

    def test_convert_string(self):
        """
        Tests that the parameter type properly converts a username string
        """

        current_user = getpass.getuser()

        param = User()
        user  = param.convert(current_user, None, None)

        self.assertEqual(
            os.getuid(),
            user,
            'User did not match',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(click.BadParameter)
    def test_convert_string_fail(self):
        """
        Tests that the parameter fails validation if the username doesn't exist
        """

        expected_user = 'i_hopefully_dont_exist'

        param = User()
        param.convert(expected_user, None, None)
    # pylint: enable=no-self-use

    def test_convert_int(self):
        """
        Tests that the parameter validates UID's exist
        """

        expected_uid = os.getuid()

        param = User()
        user  = param.convert(expected_uid, None, None)

        self.assertEqual(
            expected_uid,
            user,
            'User ID did not match',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(click.BadParameter)
    def test_convert_int_fail(self):
        """
        Tests that the parameter fails validation if the UID doesn't exist
        """

        # This should be way larger than the system limit since its 2^64
        user_id = 0x10000000000000000

        param = User()
        param.convert(user_id, None, None)
    # pylint: enable=no-self-use

class TestGroup(unittest.TestCase):
    """
    Tests for the Group parameter type
    """

    def test_convert_string(self):
        """
        Tests that the parameter converts a group name into a GID
        """

        expected_gid  = os.getgid()
        current_group = grp.getgrgid(expected_gid).gr_name

        param = Group()
        group = param.convert(current_group, None, None)

        self.assertEqual(
            expected_gid,
            group,
            'Group ID did not match',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(click.BadParameter)
    def test_convert_string_fail(self):
        """
        Tests that the parameter fails validation if the group name doesn't exist
        """

        param = Group()
        param.convert('i_hopefully_dont_exist', None, None)

    def test_convert_int(self):
        """
        Tests that the parameter validates that the GID exists
        """

        expected_gid = os.getgid()

        param = Group()
        group = param.convert(expected_gid, None, None)

        self.assertEqual(
            expected_gid,
            group,
            'Group ID did not match',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(click.BadParameter)
    def test_convert_int_fail(self):
        """
        Tests that the parameter fails validation if the GID doesn't exist
        """

        # This should be way larger than the system limit since its 2^64
        group_id = 0x10000000000000000

        param = Group()
        param.convert(group_id, None, None)
    # pylint: enable=no-self-use

if __name__ == '__main__':
    unittest.main()

