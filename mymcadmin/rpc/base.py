"""
Base implementations for JSON RPC
"""

import abc
import json

class JsonSerializable(object):
    """
    An object that is JSON serializable
    """

    metaclass = abc.ABCMeta

    JSONRPC_VERSION = '2.0'

    @property
    def data(self):
        """
        A dictionary representation of the object
        """

        return {
            'jsonrpc': self.JSONRPC_VERSION,
        }

    @property
    def json(self):
        """
        Object as a JSON string
        """

        return json.dumps(self.data)

    @abc.abstractclassmethod
    def from_json(cls, json_str):
        """
        Parse object from a JSON string
        """

