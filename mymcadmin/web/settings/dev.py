"""
Development environment settings
"""

import os.path

# pylint: disable=unused-wildcard-import, wildcard-import
from .base import *

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

