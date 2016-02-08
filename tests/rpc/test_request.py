import json
import nose
import unittest

from mymcadmin.rpc import errors, request

class TestJsonRpcRequest(unittest.TestCase):
	def setUp(self):
		self.req = request.JsonRpcRequest(
			method     = 'test',
			params     = {
				'param1': 'this is a test',
			},
			request_id = 1,
		)


	def test_get_method(self):
		self.assertEqual(
			'test',
			self.req.method,
			'JSON RPC method did not match',
		)

	def test_set_method(self):
		self.req.method = 'new_method'

		self.assertEqual(
			'new_method',
			self.req.method,
			'JSON RPC method did not match',
		)

	@nose.tools.raises(ValueError)
	def test_set_method_invalid(self):
		self.req.method = 'rpc.my_method'

	def test_get_params(self):
		self.assertEqual(
			{
				'param1': 'this is a test',
			},
			self.req.params,
			'Parameters did not match',
		)

	def test_set_params(self):
		self.req.params = {
			'param1': 'this',
			'param2': 'is',
			'param3': 'a',
			'param4': 'test',
		}

		self.assertDictEqual(
			{
				'param1': 'this',
				'param2': 'is',
				'param3': 'a',
				'param4': 'test',
			},
			self.req.params,
			'Parameters were not updated',
		)

	@nose.tools.raises(ValueError)
	def test_set_params_invalid(self):
		self.req.params = 'Bad!'

	def test_get_request_id(self):
		self.assertEqual(
			1,
			self.req.request_id,
			'Request ID did not match',
		)

	def test_set_request_id(self):
		self.req.request_id = 9001

		self.assertEqual(
			9001,
			self.req.request_id,
			'Request ID was not updated',
		)

	def test_get_data(self):
		self.assertEqual(
			{
				'jsonrpc': '2.0',
				'method':  'test',
				'id':      1,
				'params':  {
					'param1': 'this is a test',
				},
			},
			self.req.data,
			'JSON data did not match',
		)

	@nose.tools.raises(AttributeError)
	def test_set_data(self):
		self.req.data = 'bad!'

	def test_get_args(self):
		self.req.params = ['this', 'is', 'a', 'test']

		self.assertEqual(
			('this', 'is', 'a', 'test'),
			self.req.args,
			'Parameters were not properly converted',
		)

	def test_get_args_wrong_type(self):
		self.assertEqual(
			(),
			self.req.args,
			'Empty tuple not returned',
		)

	@nose.tools.raises(AttributeError)
	def test_set_args(self):
		self.req.args = 'bad!'

	def test_get_kwargs(self):
		self.assertEqual(
			{
				'param1': 'this is a test',
			},
			self.req.kwargs,
			'Parameters were not converted properly',
		)

	def test_get_kwargs_wrong_type(self):
		self.req.params = ['this', 'is', 'a', 'test']

		self.assertEqual(
			{},
			self.req.kwargs,
			'Empty dictionary was not returned',
		)

	@nose.tools.raises(AttributeError)
	def test_set_kwargs(self):
		self.req.kwargs = {}

	def test_get_json(self):
		self.assertEqual(
			json.dumps(self.req.data),
			self.req.json,
			'JSON string was not formatted correctly',
		)

	@nose.tools.raises(AttributeError)
	def test_set_json(self):
		self.req.json = 'Bad!'

	def test_from_json_single(self):
		json_str = self.req.json

		req = request.JsonRpcRequest.from_json(json_str)

		self.assertIsInstance(
			req,
			request.JsonRpcRequest,
			'Request was not of the correct type',
		)

		self.assertDictEqual(
			self.req.data,
			req.data,
			'Request data did not match',
		)

	@nose.tools.raises(errors.JsonRpcParseRequestError)
	def test_from_json_single_invalid_json(self):
		request.JsonRpcRequest.from_json('[')

	@nose.tools.raises(errors.JsonRpcInvalidRequestError)
	def test_from_json_single_no_data(self):
		request.JsonRpcRequest.from_json('[]')

	@nose.tools.raises(errors.JsonRpcInvalidRequestError)
	def test_from_json_single_non_objects(self):
		request.JsonRpcRequest.from_json('[[]]')

	@nose.tools.raises(errors.JsonRpcInvalidRequestError)
	def test_from_json_single_missing_field(self):
		request.JsonRpcRequest.from_json(
			json.dumps(
				{'jsonrpc': '2.0'}
			)
		)

	@nose.tools.raises(errors.JsonRpcInvalidRequestError)
	def test_from_json_single_extra_field(self):
		request.JsonRpcRequest.from_json(
			json.dumps(
				{
					'jsonrpc': '2.0',
					'method':  'test',
					'extra':   'Boo!',
				}
			)
		)

	@nose.tools.raises(errors.JsonRpcInvalidRequestError)
	def test_from_json_single_invalid_version(self):
		request.JsonRpcRequest.from_json(
			json.dumps(
				{
					'jsonrpc': '1.0',
					'method':  'test',
				}
			)
		)

	def test_from_json_batch(self):
		original_reqs = [
			{
				'jsonrpc': '2.0',
				'method': 'do_the_thing',
				'params': {
					'a': 1,
					'b': 2,
					'z': 26,
				},
				'id': 9001,
			},
			{
				'jsonrpc': '2.0',
				'method': 'other_thing',
				'params': {
					'oh': 'yeah',
				},
				'id': 9002,
			},
			{
				'jsonrpc': '2.0',
				'method': 'notify',
			}
		]

		reqs = request.JsonRpcRequest.from_json(
			json.dumps(original_reqs),
		)

		self.assertIsInstance(
			reqs,
			request.JsonRpcBatchRequest,
			'Batch request type did not match',
		)

		count = 0
		for req in reqs:
			self.assertEqual(
				original_reqs[count],
				req.data,
				'Request data did not match',
			)

			count += 1

class TestJsonRpcBatchRequest(unittest.TestCase):
	def test_get_json(self):
		original_req = [
			{
				'jsonrpc': '2.0',
				'method':  'test',
				'id':      90,
				'params':  [1, 2, 3, 4],
			},
			{
				'jsonrpc': '2.0',
				'method':  'boom',
			}
		]

		req = request.JsonRpcBatchRequest(
			[
				request.JsonRpcRequest.from_json(
					json.dumps(r)
				)
				for r in original_req
			]
		)

		self.assertEqual(
			json.dumps(original_req),
			req.json,
			'JSON string did not match',
		)

	def test_iterator(self):
		original_req = [
			{
				'jsonrpc': '2.0',
				'method':  'test',
				'id':      90,
				'params':  [1, 2, 3, 4],
			},
			{
				'jsonrpc': '2.0',
				'method':  'boom',
			}
		]

		original_req = [
			request.JsonRpcRequest.from_json(
				json.dumps(r)
			)
			for r in original_req
		]

		req = request.JsonRpcBatchRequest(original_req)

		count = 0
		for r in req:
			self.assertEqual(
				original_req[count].json,
				r.json,
				'JSON data did not match',
			)

			count += 1

	def test_from_json(self):
		original_req = [
			{
				'jsonrpc': '2.0',
				'method':  'test',
				'id':      90,
				'params':  [1, 2, 3, 4],
			},
			{
				'jsonrpc': '2.0',
				'method':  'boom',
			}
		]

		json_str = json.dumps(original_req)

		original_req = [
			request.JsonRpcRequest.from_json(
				json.dumps(r)
			)
			for r in original_req
		]

		req = request.JsonRpcBatchRequest.from_json(json_str)

		self.assertIsInstance(
			req,
			request.JsonRpcBatchRequest,
			'Request type did not match',
		)

		count = 0
		for r in req:
			self.assertEqual(
				original_req[count].json,
				r.json,
				'JSON data did not match',
			)

			count += 1

if __name__ == '__main__':
	unittest.main()

