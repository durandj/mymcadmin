"""
Utilities to be used for testing
"""

import asyncio
import contextlib
import functools
import unittest.mock

import click.testing

def run_async(func):
    """
    Allow a unittest to be a coroutine and still run normally
    """

    if not asyncio.iscoroutinefunction(func):
        raise RuntimeError('Test function is not a coroutine')

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        Test wrapper
        """

        event_loop = asyncio.new_event_loop()
        event_loop.run_until_complete(func(*args, **kwargs))
        event_loop.close()

    return wrapper

def apply_mock(target):
    """
    Mocks a target without naming it.

    Shorthand for:
        with unittest.mock.patch('mock_me'):
            do_the_thing()
    """

    def decorator(func):
        """
        The actual decorator
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            Test wrapper
            """

            with unittest.mock.patch(target):
                return func(*args, **kwargs)

        return wrapper
    return decorator

@contextlib.contextmanager
def mock_property(target, prop_name):
    """
    Temporarily mocks a property for an existing object and
    then restores the property after leaving the context
    scope.
    """

    target_type   = type(target)
    original_prop = getattr(target_type, prop_name)
    mock_prop     = unittest.mock.PropertyMock()

    setattr(target_type, prop_name, mock_prop)

    try:
        yield mock_prop
    finally:
        setattr(target_type, prop_name, original_prop)

# pylint: disable=invalid-name, too-few-public-methods
class CliRunnerMixin(object):
    """
    TestCase mixin for adding a CLI runner to the environment
    """

    def setUp(self):
        """
        Set up the test runner
        """

        self.cli_runner = click.testing.CliRunner()
# pylint: enable=invalid-name, too-few-public-methods

