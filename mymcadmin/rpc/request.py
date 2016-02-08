import json

from . import errors

class JsonRpcRequest(object):
	JSONRPC_VERSION = '2.0'

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
		return self._method

	@method.setter
	def method(self, value):
		if value.startswith('rpc.'):
			raise ValueError('Method names cannot begin with "rpc."')

		self._method = value

	@property
	def params(self):
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
		return self._request_id

	@request_id.setter
	def request_id(self, value):
		self._request_id = value

	@property
	def data(self):
		data = {
			'jsonrpc': self.JSONRPC_VERSION,
			'method':  self.method
		}

		if self.params:
			data['params'] = self.params

		if self.request_id:
			data['id'] = self.request_id

		return data

	@property
	def args(self):
		return tuple(self.params) if isinstance(self.params, list) else ()

	@property
	def kwargs(self):
		return self.params if isinstance(self.params, dict) else {}

	@property
	def json(self):
		return json.dumps(self.data)

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

			try:
				result.append(
					JsonRpcRequest(
						method          = req['method'],
						params          = req.get('params'),
						request_id      = req.get('id'),
						is_notification = 'id' not in req,
					)
				)
			except ValueError as e:
				raise errors.JsonRpcInvalidRequestError(str(e))

		return JsonRpcBatchRequest(result) if is_batch else result[0]

class JsonRpcBatchRequest(object):
	def __init__(self, requests):
		self.requests = requests

	@property
	def json(self):
		return json.dumps([r.data for r in self.requests])

	def __iter__(self):
		return iter(self.requests)

	@classmethod
	def from_json(cls, json_str):
		return JsonRpcRequest.from_json(json_str)

