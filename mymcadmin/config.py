"""
Configuration for the MyMCAdmin commands and backend.
"""

import json
import os.path

from . import errors

# pylint: disable=too-few-public-methods
class Config(object):
    """
    MyMCAdmin's configuration file for controlling things like where server
    instances are stored. Config files are stored in each user's home directory
    as ".mymcadminrc".
    """

    CONFIG_FILE = os.path.expanduser(
        os.path.expandvars(
            os.path.join('~', '.mymcadminrc')
        )
    )

    def __init__(self, config_file = None):
        if config_file is None:
            config_file = Config.CONFIG_FILE

        try:
            with open(config_file, 'r') as config:
                self._config = json.load(config)
        except Exception as ex:
            raise errors.ConfigurationError(
                'There was a problem loading the config file: {}',
                str(ex),
            )

    def __getattr__(self, name):
        return self._config.get(name)
# pylint: enable=too-few-public-methods

