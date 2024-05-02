import uuid
import logging
from jwt import DecodeError, ExpiredSignatureError, MissingRequiredClaimError

from fastapi import Request, HTTPException, status, responses
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.security import decode_token


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        
    async def set_body(self, request: Request):
        receive_ = await request._receive()
        async def receive():
            return receive_
        request._receive = receive

    async def dispatch(self, request, call_next):
        if request.method != 'OPTIONS':
            authorization = request.headers.get("Authorization")
            user_id = None
            if authorization is not None:
                _, _, token = authorization.partition(" ")
                try:
                    payload = decode_token(token)
                except ExpiredSignatureError:
                    return responses.JSONResponse(
                        content={'detail': 'Your token has expired. Please log in again.'},
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                except DecodeError:
                    return responses.JSONResponse(
                        content={'detail': 'Error when decoding the token. Please check your request.'},
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                except MissingRequiredClaimError:
                    return responses.JSONResponse(
                        content={'detail': 'There is no required field in your token. Please contact the administrator.'},
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                user_id = payload['sub']
            await self.set_body(request)
            request.state.request_id = request.headers.get("x-request-id")
            request_id = request.state.request_id
            body = {}
            try:
                body = await request.json()
            except:
                body = {}
            logger.info(
                "Incomming request",
                extra={
                    "request_id": request_id if request_id else None,
                    "method": str(request.method).upper(),
                    "path": str(request.url.path),
                    "params": str(request.query_params),
                    'body': body,
                    "user_id": user_id
                },
            )

        response = await call_next(request)
        return response