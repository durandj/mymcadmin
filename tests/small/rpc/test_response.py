"""
Tests for the JSON RPC response class
"""

import json
import unittest

import nose

from mymcadmin.rpc import response

class TestJsonRpcResponse(unittest.TestCase):
    """
    Tests for the JSON RPC response class
    """

    # pylint: disable=no-self-use
    @nose.tools.raises(ValueError)
    def test_constructor_missing(self):
        """
        Tests that we require certain fields
        """

        response.JsonRpcResponse()
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(ValueError)
    def test_constructor_invalid(self):
        """
        Tests that we don't allow error and result to be set
        """

        response.JsonRpcResponse(error = {}, result = {})
    # pylint: enable=no-self-use

    def test_get_result(self):
        """
        Tests that we can get the result property
        """

        resp = response.JsonRpcResponse(result = {'test': 'value'})

        self.assertDictEqual(
            {'test': 'value'},
            resp.result,
            'Response result did not match',
        )

    def test_set_result(self):
        """
        Tests that we can set the result property
        """

        resp = response.JsonRpcResponse(result = {'test': 'value'})

        resp.result = {'new': 'value'}

        self.assertDictEqual(
            {'new': 'value'},
            resp.result,
            'Result was not updated',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(ValueError)
    def test_set_result_error(self):
        """
        Tests that we can't set the result and error properties
        """

        resp = response.JsonRpcResponse(error = {'test': 'value'})

        resp.result = {'new': 'value'}
    # pylint: enable=no-self-use

    def test_get_error(self):
        """
        Tests that we can get the error property
        """

        resp = response.JsonRpcResponse(error = {'test': 'value'})

        self.assertEqual(
            {'test': 'value'},
            resp.error,
            'Response error did not match',
        )

    def test_set_error(self):
        """
        Tests that we can set the error property
        """

        resp = response.JsonRpcResponse(error = {'test': 'value'})

        resp.error = {'new': 'value'}

        self.assertEqual(
            {'new': 'value'},
            resp.error,
            'Response error did not match',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(ValueError)
    def test_set_error_error(self):
        """
        Tests that we can't set the error and result properties
        """

        resp = response.JsonRpcResponse(result = {'test': 'value'})

        resp.error = {'new': 'value'}
    # pylint: enable=no-self-use

    def test_get_response_id(self):
        """
        Tests that we can get the response_id property
        """

        resp = response.JsonRpcResponse(
            response_id = 1,
            result      = {'test': 'value'},
        )

        self.assertEqual(
            1,
            resp.response_id,
            'Response ID did not match',
        )

    def test_set_response_id(self):
        """
        Tests that we can set the response_id property
        """

        resp = response.JsonRpcResponse(result = {'test': 'value'})

        resp.response_id = 2

        self.assertEqual(
            2,
            resp.response_id,
            'Response ID was not updated',
        )

    def test_get_data_result(self):
        """
        Tests that we can get the data property
        """

        resp = response.JsonRpcResponse(
            result      = {'test': 'value'},
            response_id = 9000,
        )

        self.assertDictEqual(
            {
                'jsonrpc': '2.0',
                'result':  {'test': 'value'},
                'id':      9000,
            },
            resp.data,
            'Response data did not match',
        )

        resp = response.JsonRpcResponse(
            result      = {},
            response_id = 9001,
        )

        self.assertDictEqual(
            {
                'jsonrpc': '2.0',
                'result':  {},
                'id':      9001,
            },
            resp.data,
            'Response data did not match',
        )

        resp = response.JsonRpcResponse(
            result      = [],
            response_id = 9002,
        )

        self.assertDictEqual(
            {
                'jsonrpc': '2.0',
                'result':  [],
                'id':      9002,
            },
            resp.data,
            'Response data did not match',
        )

    def test_get_data_result_no_id(self):
        """
        Tests that we can get data with no response ID
        """

        resp = response.JsonRpcResponse(
            result = {'test': 'value'},
        )

        self.assertDictEqual(
            {
                'jsonrpc': '2.0',
                'result':  {'test': 'value'},
            },
            resp.data,
            'Response data did not match',
        )

    def test_get_data_error(self):
        """
        Tests that we get the data property with an error
        """

        resp = response.JsonRpcResponse(
            error       = {'test': 'value'},
            response_id = 9001,
        )

        self.assertDictEqual(
            {
                'jsonrpc': '2.0',
                'error':   {'test': 'value'},
                'id':      9001,
            },
            resp.data,
            'Response data did not match',
        )

    def test_get_data_error_no_id(self):
        """
        Tests that we get the error response with no response ID
        """

        resp = response.JsonRpcResponse(
            error       = {'test': 'value'},
        )

        self.assertDictEqual(
            {
                'jsonrpc': '2.0',
                'error':   {'test': 'value'},
            },
            resp.data,
            'Response data did not match',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(AttributeError)
    def test_set_data(self):
        """
        Tests that we can't set the data property
        """

        resp = response.JsonRpcResponse(
            result = {'test': 'value'},
        )

        resp.data = {'new': 'value'}
    # pylint: enable=no-self-use

    def test_from_json(self):
        """
        Tests that we can get a request from a JSON string
        """

        original_resp = {
            'jsonrpc': '2.0',
            'result':  {'test': 'value'},
            'id':      8080,
        }

        resp = response.JsonRpcResponse.from_json(json.dumps(original_resp))

        self.assertDictEqual(
            original_resp,
            resp.data,
            'Deserialized JSON RPC response did not match',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(ValueError)
    def test_from_json_missing_version(self):
        """
        Tests that we raise the correct error when the version is missing
        """

        original_resp = {
            'result': '-1.0',
        }

        response.JsonRpcResponse.from_json(json.dumps(original_resp))
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(ValueError)
    def test_from_json_invalid_version(self):
        """
        Tests that we raise the correct error when the version isn't correct
        """

        original_resp = {
            'jsonrpc': '-1.0',
            'result':  {'test': 'value'},
        }

        response.JsonRpcResponse.from_json(json.dumps(original_resp))
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(ValueError)
    def test_from_json_list(self):
        """
        Tests that we raise the correct error for an empty array
        """

        response.JsonRpcResponse.from_json('[]')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(ValueError)
    def test_from_json_extra_field(self):
        """
        Tests that we raise an error when there's extra fields in the object
        """

        original_resp = {
            'jsonrpc': '2.0',
            'result':  {'test': 'value'},
            'extra':   'value',
        }

        response.JsonRpcResponse.from_json(json.dumps(original_resp))
    # pylint: enable=no-self-use

class TestJsonRpcBatchResponse(unittest.TestCase):
    """
    Tests for the JsonRpcBatchResponse class
    """

    def test_get_data(self):
        """
        Tests that we can get the data property
        """

        original_resp = [
            response.JsonRpcResponse(
                response_id = 9001, result = {'test': 'value'}
            ),
            response.JsonRpcResponse(
                response_id = 9002, error = 'Bad things!',
            ),
            response.JsonRpcResponse(
                result = {'more': 'values'},
            ),
        ]

        resp = response.JsonRpcBatchResponse(original_resp)

        original_resp = [r.data for r in original_resp]

        self.assertListEqual(
            original_resp,
            resp.data,
            'Batch response data did not match',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(AttributeError)
    def test_set_data(self):
        """
        Tests that we can't set the data property
        """

        original_resp = [
            response.JsonRpcResponse(
                response_id = 9001, result = {'test': 'value'}
            ),
            response.JsonRpcResponse(
                response_id = 9002, error = 'Bad things!',
            ),
            response.JsonRpcResponse(
                result = {'more': 'values'},
            ),
        ]

        resp = response.JsonRpcBatchResponse(original_resp)
        resp.data = []
    # pylint: enable=no-self-use

    def test_get_json(self):
        """
        Test that we can get the JSON object
        """

        original_resp = [
            response.JsonRpcResponse(
                response_id = 9001, result = {'test': 'value'}
            ),
            response.JsonRpcResponse(
                response_id = 9002, error = 'Bad things!',
            ),
            response.JsonRpcResponse(
                result = {'more': 'values'},
            ),
        ]

        resp = response.JsonRpcBatchResponse(original_resp)

        original_resp = [r.data for r in original_resp]

        self.assertListEqual(
            original_resp,
            json.loads(resp.json),
            'Serialized JSON string did not match',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(AttributeError)
    def test_set_json(self):
        """
        Tests that we can't set the JSON property
        """

        original_resp = [
            response.JsonRpcResponse(
                response_id = 9001, result = {'test': 'value'}
            ),
            response.JsonRpcResponse(
                response_id = 9002, error = 'Bad things!',
            ),
            response.JsonRpcResponse(
                result = {'more': 'values'},
            ),
        ]

        resp = response.JsonRpcBatchResponse(original_resp)
        resp.json = 'bad!'
    # pylint: enable=no-self-use

    def test_iter(self):
        """
        Tests that we can iterate over the requests
        """

        original_resp = [
            response.JsonRpcResponse(
                response_id = 9001, result = {'test': 'value'}
            ),
            response.JsonRpcResponse(
                response_id = 9002, error = 'Bad things!',
            ),
            response.JsonRpcResponse(
                result = {'more': 'values'},
            ),
        ]

        resps = response.JsonRpcBatchResponse(original_resp)

        original_resp = [r.data for r in original_resp]

        count = 0
        for resp in resps:
            self.assertDictEqual(
                original_resp[count],
                resp.data,
                'Response data did not match',
            )

            count += 1

if __name__ == '__main__':
    unittest.main()

