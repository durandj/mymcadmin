import json

class JsonRpcResponse(object):
    JSONRPC_VERSION = '2.0'
    POSSIBLE_FIELDS = set(['jsonrpc', 'id', 'result', 'error'])

    def __init__(self, result = None, error = None, response_id = None):
        self._result      = result
        self._error       = error
        self._response_id = response_id

        if result is None and error is None:
            raise ValueError('Either result or error must be set')

        if result is not None and error is not None:
            raise ValueError('Can\'t set result and error')

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        if self.error and value is not None:
            raise ValueError('Can\'t set result and error')

        self._result = value

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        if self.result and value is not None:
            raise ValueError('Can\'t set result and error')

        self._error = value

    @property
    def response_id(self):
        return self._response_id

    @response_id.setter
    def response_id(self, value):
        self._response_id = value

    @property
    def data(self):
        data = {
            'jsonrpc': self.JSONRPC_VERSION,
        }

        if self.result:
            data['result'] = self.result

        if self.error:
            data['error'] = self.error

        if self.response_id:
            data['id'] = self.response_id

        return data

    @property
    def json(self):
        return json.dumps(self.data)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)

        if not isinstance(data, dict):
            raise ValueError('Data should be a dict')

        if 'jsonrpc' not in data:
            raise ValueError('Missing JSON RPC version')

        if data['jsonrpc'] != '2.0':
            raise ValueError(
                'Unsupported JSON RPC version {}'.format(data['jsonrpc'])
            )

        fields = set(data.keys())
        if fields.difference(cls.POSSIBLE_FIELDS):
            raise ValueError(
                'Extra field: {}'.format(
                    fields.difference(cls.POSSIBLE_FIELDS)
                )
            )

        return cls(
            result      = data.get('result'),
            error       = data.get('error'),
            response_id = data.get('id'),
        )

class JsonRpcBatchResponse(object):
    def __init__(self, responses):
        self.responses = responses

    @property
    def data(self):
        return [r.data for r in self.responses]

    @property
    def json(self):
        return json.dumps(self.data)

    def __iter__(self):
        return iter(self.responses)

class JsonRpcErrorResponse(JsonRpcResponse):
    def __init__(self, code, message, request_id = None):
        super(JsonRpcErrorResponse, self).__init__(
            response_id = request_id,
            error      = {
                'code':    code,
                'message': message,
            }
        )

class JsonRpcParseErrorResponse(JsonRpcErrorResponse):
    def __init__(self):
        super(JsonRpcParseErrorResponse, self).__init__(
            -32700,
            'Parse error',
        )

class JsonRpcInvalidRequestResponse(JsonRpcErrorResponse):
    def __init__(self, request_id = None):
        super(JsonRpcInvalidRequestResponse, self).__init__(
            -32600,
            'Invalid Request',
            request_id = request_id,
        )

class JsonRpcMethodNotFoundResponse(JsonRpcErrorResponse):
    def __init__(self, request_id):
        super(JsonRpcMethodNotFoundResponse, self).__init__(
            -32601,
            'Method not found',
            request_id = request_id,
        )

class JsonRpcServerErrorResponse(JsonRpcErrorResponse):
    def __init__(self, request_id):
        super(JsonRpcServerErrorResponse, self).__init__(
            -32000,
            'Server error',
            request_id = request_id,
        )

