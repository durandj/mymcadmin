"""
JSON RPC requests
"""

import json

from . import base, errors

class JsonRpcRequest(base.JsonSerializable):
    """
    A request via JSON RPC
    """

    REQUIRED_FIELDS = set(['jsonrpc', 'method'])
    POSSIBLE_FIELDS = set(['jsonrpc', 'method', 'params', 'id'])

    def __init__(self, method = None, params = None,
                 request_id = None, is_notification = None):
        self._method         = method
        self._params         = params
        self._request_id     = request_id
        self.is_notification = is_notification

    @property
    def method(self):
        """
        The requested method
        """

        return self._method

    @method.setter
    def method(self, value):
        if value.startswith('rpc.'):
            raise ValueError('Method names cannot begin with "rpc."')

        self._method = value

    @property
    def params(self):
        """
        The parameters for the request
        """

        return self._params

    @params.setter
    def params(self, value):
        if value is not None and not isinstance(value, (list, tuple, dict)):
            raise ValueError('Invalid parameter collection type')

        value = list(value) if isinstance(value, tuple) else value

        if value is not None:
            self._params = value

    @property
    def request_id(self):
        """
        The ID of the request
        """

        return self._request_id

    @request_id.setter
    def request_id(self, value):
        self._request_id = value

    @property
    def data(self):
        data = super(JsonRpcRequest, self).data
        data['method'] = self.method

        if self.params:
            data['params'] = self.params

        if self.request_id:
            data['id'] = self.request_id

        return data

    @property
    def args(self):
        """
        The parameters for the request as a tuple
        """

        return tuple(self.params) if isinstance(self.params, list) else ()

    @property
    def kwargs(self):
        """
        The parameters for the request as a dictionary
        """

        return self.params if isinstance(self.params, dict) else {}

    @classmethod
    def from_json(cls, json_str):
        try:
            data = json.loads(json_str)
        except (json.JSONDecodeError, TypeError, ValueError):
            raise errors.JsonRpcParseRequestError()

        is_batch = isinstance(data, list)
        data     = data if is_batch else [data]

        if not data:
            raise errors.JsonRpcInvalidRequestError('Expected JSON request')

        if not all(isinstance(d, dict) for d in data):
            raise errors.JsonRpcInvalidRequestError('Expected Json object')

        result = []
        for req in data:
            req_keys = set(req.keys())

            if not cls.REQUIRED_FIELDS.issubset(req_keys):
                raise errors.JsonRpcInvalidRequestError(
                    'Missing required fields: {}',
                    cls.REQUIRED_FIELDS.difference(req_keys),
                )

            if not cls.POSSIBLE_FIELDS.issuperset(req_keys):
                raise errors.JsonRpcInvalidRequestError(
                    'Unexpected fields: {}',
                    req_keys.difference(cls.POSSIBLE_FIELDS),
                )

            if req['jsonrpc'] != cls.JSONRPC_VERSION:
                raise errors.JsonRpcInvalidRequestError(
                    'Invalid JSON RPC version',
                )

            result.append(
                JsonRpcRequest(
                    method          = req['method'],
                    params          = req.get('params'),
                    request_id      = req.get('id'),
                    is_notification = 'id' not in req,
                )
            )

        return JsonRpcBatchRequest(result) if is_batch else result[0]

class JsonRpcBatchRequest(base.JsonSerializable):
    """
    A batch of JSON RPC requests
    """

    def __init__(self, requests):
        self.requests = requests

    @property
    def data(self):
        return [r.data for r in self.requests]

    def __iter__(self):
        return iter(self.requests)

    @classmethod
    def from_json(cls, json_str):
        """
        Build a request from a JSON string
        """

        return JsonRpcRequest.from_json(json_str)

