from . import response
from .. import errors

class JsonRpcError(errors.MyMCAdminError):
	"""
	General JSON RPC error
	"""

	def __init__(self, message, *args, **kwargs):
		super(JsonRpcError, self).__init__(message, *args, **kwargs)

	@property
	def response(self):
		return getattr(self, 'RESPONSE_TYPE')()

class JsonRpcParseRequestError(JsonRpcError):
	"""
	Throw when there's a proble parsing the JSON RPC request
	"""

	RESPONSE_TYPE = response.JsonRpcParseErrorResponse

	def __init__(self):
		super(JsonRpcParseRequestError, self).__init__('Malformed JSON')

class JsonRpcInvalidRequestError(JsonRpcError):
	"""
	Thrown when an invalid request is sent via JSON RPC
	"""

	RESPONSE_TYPE = response.JsonRpcInvalidRequestResponse

class JsonRpcMethodNotFoundError(JsonRpcError):
	"""
	Thrown when a request is received that has a method we don't implement
	"""

	RESPONSE_TYPE = response.JsonRpcMethodNotFoundResponse

	def __init__(self, request_id, message, *args, **kwargs):
		super(JsonRpcMethodNotFoundError, self).__init__(
			message,
			*args,
			**kwargs
		)

		self.request_id = request_id

	@property
	def response(self):
		return self.RESPONSE_TYPE(self.request_id)

class JsonRpcServerError(JsonRpcError):
	"""
	Thrown when the server encounters an error when
	generating a response
	"""

	RESPONSE_TYPE = response.JsonRpcServerErrorResponse

	def __init__(self, request_id, message, *args, **kwargs):
		super(JsonRpcServerError, self).__init__(
			message,
			*args,
			**kwargs
		)

		self.request_id = request_id

	@property
	def response(self):
		return self.RESPONSE_TYPE(self.request_id)

