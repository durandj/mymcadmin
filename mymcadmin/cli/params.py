"""
Custom parameter types for MyMCAdmin
"""

import grp
import pwd

import click

class User(click.ParamType):
    """
    A system user defined by its username or UID
    """

    name = 'user'

    def convert(self, value, param, ctx):
        try:
            if isinstance(value, int):
                # This call should fail if the UID doesn't exist
                pwd.getpwuid(value)
                return value
            else:
                return pwd.getpwnam(value).pw_uid
        except KeyError:
            self.fail('User {} does not exist'.format(value))

class Group(click.ParamType):
    """
    A system user group defined by its name or GID
    """

    name = 'group'

    def convert(self, value, param, ctx):
        try:
            if isinstance(value, int):
                # This call should fail if the GID doesn't exist
                grp.getgrgid(value)
                return value
            else:
                return grp.getgrnam(value).gr_gid
        except (KeyError, OverflowError):
            self.fail('Group {} does not exist'.format(value))

