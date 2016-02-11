"""
Utilities common to the entire system
"""

import logging

def setup_logging():
    """
    Setup the logging system
    """

    logging.basicConfig(
        datefmt = '%Y-%m-%d %H:%M:%S',
        format  = '%(asctime)s %(levelname)s %(message)s',
        level   = logging.INFO,
    )

