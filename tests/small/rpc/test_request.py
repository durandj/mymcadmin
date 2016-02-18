"""
Tests for the JSON RPC request classes
"""

import json
import unittest

import nose

from mymcadmin.rpc import errors, request

# pylint: disable=too-many-public-methods
class TestJsonRpcRequest(unittest.TestCase):
    """
    Tests for the JsonRpcRequest class
    """

    def setUp(self):
        self.req = request.JsonRpcRequest(
            method     = 'test',
            params     = {
                'param1': 'this is a test',
            },
            request_id = 1,
        )


    def test_get_method(self):
        """
        Tests that we can get the method property
        """

        self.assertEqual(
            'test',
            self.req.method,
            'JSON RPC method did not match',
        )

    def test_set_method(self):
        """
        Tests that we can set the method property
        """

        self.req.method = 'new_method'

        self.assertEqual(
            'new_method',
            self.req.method,
            'JSON RPC method did not match',
        )

    @nose.tools.raises(ValueError)
    def test_set_method_invalid(self):
        """
        Tests that we don't allow methods that start with "rpc."
        """

        self.req.method = 'rpc.my_method'

    def test_get_params(self):
        """
        Tests that we can get the params property
        """

        self.assertEqual(
            {
                'param1': 'this is a test',
            },
            self.req.params,
            'Parameters did not match',
        )

    def test_set_params(self):
        """
        Tests that we can set the params property
        """

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
        """
        Tests that we don't allow strings as parameters
        """

        self.req.params = 'Bad!'

    def test_get_request_id(self):
        """
        Tests that we can get the request_id property
        """

        self.assertEqual(
            1,
            self.req.request_id,
            'Request ID did not match',
        )

    def test_set_request_id(self):
        """
        Tests that we can set the request_id property
        """

        self.req.request_id = 9001

        self.assertEqual(
            9001,
            self.req.request_id,
            'Request ID was not updated',
        )

    def test_get_data(self):
        """
        Tests that we can get the data property
        """

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
        """
        Tests that we can't set the data property
        """

        self.req.data = 'bad!'

    def test_get_args(self):
        """
        Tests that we can get the parameters as a tuple
        """

        self.req.params = ['this', 'is', 'a', 'test']

        self.assertEqual(
            ('this', 'is', 'a', 'test'),
            self.req.args,
            'Parameters were not properly converted',
        )

    def test_get_args_wrong_type(self):
        """
        Tests that we default to an empty tuple if params were an object
        """

        self.assertEqual(
            (),
            self.req.args,
            'Empty tuple not returned',
        )

    @nose.tools.raises(AttributeError)
    def test_set_args(self):
        """
        Tests that we cant set the args property
        """

        self.req.args = 'bad!'

    def test_get_kwargs(self):
        """
        Tests that we can get the params as kwargs
        """

        self.assertEqual(
            {
                'param1': 'this is a test',
            },
            self.req.kwargs,
            'Parameters were not converted properly',
        )

    def test_get_kwargs_wrong_type(self):
        """
        Tests that we can default to an empty dictionary
        """

        self.req.params = ['this', 'is', 'a', 'test']

        self.assertEqual(
            {},
            self.req.kwargs,
            'Empty dictionary was not returned',
        )

    @nose.tools.raises(AttributeError)
    def test_set_kwargs(self):
        """
        Tests that we can't set the kwargs property
        """

        self.req.kwargs = {}

    def test_from_json_single(self):
        """
        Tests that we can get a single request from a JSON string
        """

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

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.JsonRpcParseRequestError)
    def test_from_json_invalid_json(self):
        """
        Tests that we raise the correct error for invalid JSON
        """

        request.JsonRpcRequest.from_json('[')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.JsonRpcInvalidRequestError)
    def test_from_json_single_no_data(self):
        """
        Tests that we raise the correct error for an empty request
        """

        request.JsonRpcRequest.from_json('[]')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.JsonRpcInvalidRequestError)
    def test_from_json_single_lists(self):
        """
        Tests that we raise the correct error when receiving lists as requests
        """

        request.JsonRpcRequest.from_json('[[]]')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.JsonRpcInvalidRequestError)
    def test_from_json_missing_field(self):
        """
        Tests that we raise the correct error when missing a required field
        """

        request.JsonRpcRequest.from_json(
            json.dumps(
                {'jsonrpc': '2.0'}
            )
        )
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.JsonRpcInvalidRequestError)
    def test_from_json_extra_field(self):
        """
        Tests that we raise the correct error when given extra fields
        """

        request.JsonRpcRequest.from_json(
            json.dumps(
                {
                    'jsonrpc': '2.0',
                    'method':  'test',
                    'extra':   'Boo!',
                }
            )
        )
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.JsonRpcInvalidRequestError)
    def test_from_json_invalid_version(self):
        """
        Tests that we raise the correct error when given an invalid version
        """

        request.JsonRpcRequest.from_json(
            json.dumps(
                {
                    'jsonrpc': '1.0',
                    'method':  'test',
                }
            )
        )
    # pylint: enable=no-self-use

    def test_from_json_batch(self):
        """
        Tests that we create a batch request from a JSON string
        """

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
# pylint: enable=too-many-public-methods

class TestJsonRpcBatchRequest(unittest.TestCase):
    """
    Tests for the JsonRpcBatchRequest class
    """

    def test_iterator(self):
        """
        Tests that we can iterate over every request
        """

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

        batch_req = request.JsonRpcBatchRequest(original_req)

        count = 0
        for req in batch_req:
            self.assertEqual(
                original_req[count].json,
                req.json,
                'JSON data did not match',
            )

            count += 1

    def test_from_json(self):
        """
        Tests that we can get a batch request from a JSON string
        """

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

        batch_req = request.JsonRpcBatchRequest.from_json(json_str)

        self.assertIsInstance(
            batch_req,
            request.JsonRpcBatchRequest,
            'Request type did not match',
        )

        count = 0
        for req in batch_req:
            self.assertEqual(
                original_req[count].json,
                req.json,
                'JSON data did not match',
            )

            count += 1

if __name__ == '__main__':
    unittest.main()

