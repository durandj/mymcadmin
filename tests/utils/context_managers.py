"""
Context manager utilities for tests
"""

import contextlib
import unittest.mock

@contextlib.contextmanager
def mock_property(target, prop_name):
    """
    Temporarily mocks a property for an existing object and then restores the
    property after leaving the context scope.
    """

    target_type   = type(target)
    original_prop = getattr(target_type, prop_name)
    mock_prop     = unittest.mock.PropertyMock()

    setattr(target_type, prop_name, mock_prop)

    try:
        yield mock_prop
    finally:
        setattr(target_type, prop_name, original_prop)

