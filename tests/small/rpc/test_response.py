import json
import nose
import unittest

from mymcadmin.rpc import response

class TestJsonRpcResponse(unittest.TestCase):
    @nose.tools.raises(ValueError)
    def test_constructor_missing(self):
        resp = response.JsonRpcResponse()

    @nose.tools.raises(ValueError)
    def test_constructor_invalid(self):
        resp = response.JsonRpcResponse(error = {}, result = {})

    def test_get_result(self):
        resp = response.JsonRpcResponse(result = {'test': 'value'})

        self.assertDictEqual(
            {'test': 'value'},
            resp.result,
            'Response result did not match',
        )

    def test_set_result(self):
        resp = response.JsonRpcResponse(result = {'test': 'value'})

        resp.result = {'new': 'value'}

        self.assertDictEqual(
            {'new': 'value'},
            resp.result,
            'Result was not updated',
        )

    @nose.tools.raises(ValueError)
    def test_set_result_error(self):
        resp = response.JsonRpcResponse(error = {'test': 'value'})

        resp.result = {'new': 'value'}

    def test_get_error(self):
        resp = response.JsonRpcResponse(error = {'test': 'value'})

        self.assertEqual(
            {'test': 'value'},
            resp.error,
            'Response error did not match',
        )

    def test_set_error(self):
        resp = response.JsonRpcResponse(error = {'test': 'value'})

        resp.error = {'new': 'value'}

        self.assertEqual(
            {'new': 'value'},
            resp.error,
            'Response error did not match',
        )

    @nose.tools.raises(ValueError)
    def test_set_error_error(self):
        resp = response.JsonRpcResponse(result = {'test': 'value'})

        resp.error = {'new': 'value'}

    def test_get_response_id(self):
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
        resp = response.JsonRpcResponse(result = {'test': 'value'})

        resp.response_id = 2

        self.assertEqual(
            2,
            resp.response_id,
            'Response ID was not updated',
        )

    def test_get_data_result(self):
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

    def test_get_data_result_no_id(self):
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

    @nose.tools.raises(AttributeError)
    def test_set_data(self):
        resp = response.JsonRpcResponse(
            result = {'test': 'value'},
        )

        resp.data = {'new': 'value'}

    def test_get_json(self):
        resp = response.JsonRpcResponse(
            result = {'test': 'value'},
        )

        self.assertDictEqual(
            {
                'jsonrpc': '2.0',
                'result':  {'test': 'value'},
            },
            json.loads(resp.json),
            'Serialized JSON string did not match',
        )

    @nose.tools.raises(AttributeError)
    def test_set_json(self):
        resp = response.JsonRpcResponse(
            result = {'test': 'value'},
        )

        resp.json = {'new': 'value'}

    def test_from_json(self):
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

    @nose.tools.raises(ValueError)
    def test_from_json_missing_version(self):
        original_resp = {
            'result': '-1.0',
        }

        response.JsonRpcResponse.from_json(json.dumps(original_resp))

    @nose.tools.raises(ValueError)
    def test_from_json_invalid_version(self):
        original_resp = {
            'jsonrpc': '-1.0',
            'result':  {'test': 'value'},
        }

        response.JsonRpcResponse.from_json(json.dumps(original_resp))

    @nose.tools.raises(ValueError)
    def test_from_json_list(self):
        response.JsonRpcResponse.from_json('[]')

    @nose.tools.raises(ValueError)
    def test_from_json_extra_field(self):
        original_resp = {
            'jsonrpc': '2.0',
            'result':  {'test': 'value'},
            'extra':   'value',
        }

        response.JsonRpcResponse.from_json(json.dumps(original_resp))

class TestJsonRpcBatchResponse(unittest.TestCase):
    def test_get_data(self):
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

    @nose.tools.raises(AttributeError)
    def test_set_data(self):
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

    def test_get_json(self):
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

    @nose.tools.raises(AttributeError)
    def test_set_json(self):
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

    def test_iter(self):
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

