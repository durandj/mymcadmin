"""
Utility decorators for tests
"""

import asyncio
import functools
import unittest.mock

def run_async(func):
    """
    Allow a unit test to be run as a coroutine. Note that this expects to be
    used with the EventLoopMixin
    """

    if not asyncio.iscoroutinefunction(func):
        raise RuntimeError('Test function must be a coroutine')

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))

    return _wrapper

def apply_mock(target):
    """
    Mocks a target without passing it to the test function.

    Shorthand for:
        with unittest.mock.patch('mock_me'):
            do_the_thing()
    """

    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            with unittest.mock.patch(target):
                return func(*args, **kwargs)

        return _wrapper
    return _decorator

