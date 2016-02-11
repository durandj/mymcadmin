import asyncio
import json
import logging
import nose
import unittest
import unittest.mock

from ... import utils

from mymcadmin.rpc import (
    Dispatcher,
    JsonRpcBatchResponse,
    JsonRpcResponse,
    JsonRpcResponseManager,
)

from mymcadmin.rpc.response import (
    JsonRpcMethodNotFoundResponse,
    JsonRpcParseErrorResponse,
    JsonRpcServerErrorResponse,
)

class TestJsonRpcResponseManager(unittest.TestCase):
    @utils.run_async
    async def test_handle_single_string(self):
        req = json.dumps(
            {
                'jsonrpc': '2.0',
                'method':  'testification',
                'params':  {'test': 'value'},
                'id':      10,
            }
        )

        await self._run_single_req(req, 10)

    @utils.run_async
    async def test_handle_single_bytes(self):
        req = json.dumps(
            {
                'jsonrpc': '2.0',
                'method':  'testification',
                'params':  {'test': 'value'},
                'id':      10,
            }
        ).encode('utf-8')

        await self._run_single_req(req, 10)

    @utils.run_async
    async def test_handle_batch(self):
        req = json.dumps(
            [
                {
                    'jsonrpc': '2.0',
                    'method':  'testification',
                    'params':  {'test': 'value'},
                    'id':      10,
                },
                {
                    'jsonrpc': '2.0',
                    'method':  'notify',
                },
            ]
        )

        mock_testification_handler = unittest.mock.Mock()
        mock_testification_handler.return_value = {'Mishief': 'managed'}

        mock_notify_handler = unittest.mock.Mock()
        mock_notify_handler.return_value = [1, 2, 3]

        dispatcher = Dispatcher(
            methods = {
                'testification': asyncio.coroutine(mock_testification_handler),
                'notify':        asyncio.coroutine(mock_notify_handler),
            },
        )

        resp = await JsonRpcResponseManager.handle(req, dispatcher)

        self.assertIsInstance(
            resp,
            JsonRpcBatchResponse,
            'Response was not the right type',
        )

        self.assertListEqual(
            [10],
            [r.response_id for r in resp],
            'Response ID\'s did not match',
        )

        self.assertListEqual(
            [{'Mishief': 'managed'}],
            [r.result for r in resp],
            'Response result did not match',
        )

        mock_testification_handler.assert_called_with(test = 'value')

        mock_notify_handler.assert_called_with()

    @utils.run_async
    async def test_handle_notifications(self):
        req = json.dumps(
            {
                'jsonrpc': '2.0',
                'method':  'notify',
            }
        )

        mock_handler = unittest.mock.Mock()
        mock_handler.return_value = {'Mischief': 'managed'}

        dispatcher = Dispatcher(
            methods = {'notify': mock_handler}
        )

        resp = await JsonRpcResponseManager.handle(req, dispatcher)

        self.assertIsNone(
            resp,
            'Notifications did not return an empty response',
        )

    @utils.run_async
    async def test_handle_invalid_json(self):
        dispatcher = Dispatcher()

        resp = await JsonRpcResponseManager.handle('[', dispatcher)

        self.assertLogs(level = logging.ERROR)

        self.assertIsInstance(
            resp,
            JsonRpcParseErrorResponse,
            'Error response was not the correct type',
        )

    @utils.run_async
    async def test_handle_missing_method(self):
        req = json.dumps(
            {
                'jsonrpc': '2.0',
                'method':  'bad',
                'id':      9001,
            }
        )

        dispatcher = Dispatcher()

        resp = await JsonRpcResponseManager.handle(req, dispatcher)

        self.assertIsInstance(
            resp,
            JsonRpcMethodNotFoundResponse,
            'Error response was not the correct type',
        )

    @utils.run_async
    async def test_handle_server_error(self):
        req = json.dumps(
            {
                'jsonrpc': '2.0',
                'method':  'boom',
                'id':      80,
            }
        )

        async def boom():
            raise RuntimeError('Boom!')

        dispatcher = Dispatcher(
            methods = {'boom': boom},
        )

        resp = await JsonRpcResponseManager.handle(req, dispatcher)

        self.assertIsInstance(
            resp,
            JsonRpcServerErrorResponse,
            'Error response was not the correct type',
        )

    async def _run_single_req(self, req, response_id):
        mock_handler = unittest.mock.Mock()
        mock_handler.return_value = {'mischief': 'managed'}

        dispatcher = Dispatcher(
            methods = {
                'testification': asyncio.coroutine(mock_handler),
            },
        )

        resp = await JsonRpcResponseManager.handle(req, dispatcher)

        self.assertIsInstance(
            resp,
            JsonRpcResponse,
            'Invalid response type',
        )

        self.assertEqual(
            response_id,
            resp.response_id,
            'Response ID did not match',
        )

        self.assertDictEqual(
            {'mischief': 'managed'},
            resp.result,
            'Response data did not match',
        )

        mock_handler.assert_called_with(
            test = 'value',
        )

if __name__ == '__main__':
    unittest.main()

