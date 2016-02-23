"""
Development environment settings
"""

import os.path

# pylint: disable=unused-wildcard-import, wildcard-import
from .base import *

RUNTIME_DIR = os.path.join(BASE_DIR, 'runtime')
if not os.path.exists(RUNTIME_DIR):
    os.mkdir(RUNTIME_DIR)

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(RUNTIME_DIR, 'db.sqlite3'),
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

WEBPACK_LOADER['DEFAULT']['STATS_FILE'] = os.path.join(
    RUNTIME_DIR,
    'webpack-stats.json',
)

