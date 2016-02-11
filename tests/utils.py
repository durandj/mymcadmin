"""
Utilities to be used for testing
"""

import asyncio
import functools
import unittest.mock

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

