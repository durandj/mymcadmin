"""
Decorators to assist in the use of the JSON RPC interface
"""

import functools

from . import errors

def required_param(name):
    """
    Adds a check for a required JSON RPC parameter. This works for keyword
    parameters only.
    """

    def _decorator(func):
        @functools.wraps(func)
        async def _wrapper(*args, **kwargs):
            if name not in kwargs:
                raise errors.JsonRpcInvalidRequestError(
                    'Missing required parameter {}',
                    name
                )

            return await func(*args, **kwargs)

        return _wrapper

    return _decorator

