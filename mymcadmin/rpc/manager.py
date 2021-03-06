"""
JSON RPC response manager for handling requests
"""

import logging

from . import errors, request, response

class JsonRpcResponseManager(object):
    """
    JSON RPC response manager for handling requests
    """

    @classmethod
    async def handle(cls, request_str, dispatcher):
        """
        Handle a JSON RPC request
        """

        if isinstance(request_str, bytes):
            request_str = request_str.decode('utf-8')

        try:
            req = request.JsonRpcRequest.from_json(request_str)
        except errors.JsonRpcError as ex:
            logging.exception(ex.message, exc_info = True)

            return ex.response

        return await cls.handle_request(req, dispatcher)

    @classmethod
    async def handle_request(cls, rpc_request, dispatcher):
        """
        Backend handling of a request
        """

        if not isinstance(rpc_request, request.JsonRpcBatchRequest):
            rpc_request = [rpc_request]

        responses = await cls._get_responses(rpc_request, dispatcher)
        responses = [resp for resp in responses if resp is not None]

        # Happens when we recieve a batch of notifications
        if not responses:
            return

        if isinstance(rpc_request, request.JsonRpcBatchRequest):
            return response.JsonRpcBatchResponse(responses)
        else:
            return responses[0]

    @classmethod
    async def _get_responses(cls, requests, dispatcher):
        responses = []

        # pylint: disable=broad-except
        for req in requests:
            try:
                try:
                    method = dispatcher[req.method]
                except KeyError:
                    raise errors.JsonRpcMethodNotFoundError(
                        req.request_id,
                        'Unknown method: {}',
                        req.method,
                    )

                result = await method(*req.args, **req.kwargs)
                resp   = response.JsonRpcResponse(
                    response_id = req.request_id,
                    result      = result,
                )

                if not req.is_notification:
                    responses.append(resp)
            except errors.JsonRpcError as ex:
                logging.exception(ex.message, exc_info = True)

                resp = ex.response
                if not req.is_notification:
                    responses.append(resp)
            except Exception as ex:
                logging.exception(str(ex), exc_info = True)

                resp = errors.JsonRpcServerError(
                    req.request_id,
                    str(ex),
                ).response

                if not req.is_notification:
                    responses.append(resp)
        # pylint: enable=broad-except

        return responses

