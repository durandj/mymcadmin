"""
Utilities common to the entire system
"""

import logging

def setup_logging():
    """
    Setup the logging system
    """

    # TODO(durandj): make log level changeable
    # TODO(durandj): make log format customizable
    logging.basicConfig(
        datefmt = '%Y-%m-%d %H:%M:%S',
        format  = '%(asctime)s %(levelname)s %(message)s',
        level   = logging.INFO,
    )

