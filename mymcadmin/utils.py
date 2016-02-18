"""
Utilities common to the entire system
"""

import logging
import pwd

def setup_logging():
    """
    Setup the logging system
    """

    logging.basicConfig(
        datefmt = '%Y-%m-%d %H:%M:%S',
        format  = '%(asctime)s %(levelname)s %(message)s',
        level   = logging.INFO,
    )

def get_user_home(user = None):
    """
    Get the home directory for a user. Defaults to current user
    """

    home_func = pwd.getpwuid if isinstance(user, int) else pwd.getpwnam

    return home_func(user).pw_dir

