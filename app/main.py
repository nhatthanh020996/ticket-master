import logging
import math
from contextlib import asynccontextmanager
import jwt

from fastapi import FastAPI, Request, status, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware, db
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis


from .generics.middlewares.logging_middlewares import LoggingMiddleware
from .generics.exceptions import APIException
from .generics import redis_connection, async_es, settings
from .generics.utils.alert_notification import send_discord_message

from .generics.utils.security import decode_token
from .users.routers import user_router
from .auth.routers import auth_router


uvicorn_error = logging.getLogger("uvicorn.error")
uvicorn_error.disabled = True
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.disabled = True
logger = logging.getLogger(__name__)

async def user_id_identifier(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header is not None:
        header_parts = auth_header.split()
        if len(header_parts) == 2 and header_parts[0].lower() == "bearer":
            token = header_parts[1]
            try:
                payload = decode_token(token)
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your token has expired. Please log in again.",
                )
            except jwt.DecodeError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Error when decoding the token. Please check your request.",
                )
            except jwt.MissingRequiredClaimError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="There is no required field in your token. Please contact the administrator.",
                )
            return payload['sub']


async def rate_limit_http_callback(request: Request, response: Response, pexpire: int):
    """
    default callback when too many requests
    :param request:
    :param pexpire: The remaining milliseconds
    :param response:
    :return:
    """
    username = request.state.user['username'] if hasattr(request.state, 'user') else ''
    error_message = f"""
    **Environment:** {settings.ENVIRONMENT}\n**Path:** {str(request.url.path)}\n**Username:** {str(username)}\n
    """
    send_discord_message(settings.DISCORD_WEBHOOK, error_message, 'Rate Limiter')
    expire = math.ceil(pexpire / 1000)
    raise HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests", headers={"Retry-After": str(expire)}
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await FastAPILimiter.init(
        redis.from_url(f'redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}'), 
        identifier=user_id_identifier,
        http_callback=rate_limit_http_callback
    )
    assert await async_es.ping(), 'ES server has problem, please check the ES server :('
    assert await redis_connection.ping(), 'Redis server has problem, please check the redis server :('
    logger.info("Webserver's ready to listen incomming requests!")
    yield
    await FastAPILimiter.close()
    await async_es.close()
    logger.info('Closed elasticsearch client successfully!')
    await redis_connection.close()
    logger.info('Closed redis client successfully!')

app = FastAPI(
    title="DMS Processor",
    description="Call me more",
    version="0.0.1",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    lifespan=lifespan
)

add_pagination(app)
disable_installed_extensions_check()


app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=str(settings.DATABASE_URI),
    engine_args={
        "echo": False,
        "pool_pre_ping": True,
        "pool_size": 8,
        "max_overflow": 64,
    },
    commit_on_exit=True
)
app.add_middleware(LoggingMiddleware)

@app.exception_handler(APIException)
async def http_exception_handler(request: Request, exc: APIException):
    request_id = request.state.request_id
    return JSONResponse(
        status_code=exc.status, 
        content={"message": exc.message, "error_code": exc.error_code, 'trace_id': request_id}
    )


@app.exception_handler(Exception)
async def http_exception_handler(request: Request, exc: Exception):
    request_id = request.state.request_id
    body = {}
    try:
        body = await request.json()
    except:
        body = {}
    username = request.state.user['username'] if hasattr(request.state, 'user') else ''
    logger.exception(
        'Unexpected Exception Occurs',
        extra={
            'request_id': request_id,
            "method": str(request.method).upper(),
            "path": str(request.url.path),
            "params": str(request.query_params),
            'body': body,
            "user_id": username
        }
    )
    if settings.ENABLE_ALERT_NOTIFICATION:
        error_message = f"""
        **Environment:** {settings.ENVIRONMENT}\n**Request ID:** {str(request_id)}\n**Path:** {str(request.url.path)}\n**Body:** {str(body)}\n**User ID:** {str(username)}
        ```\{str(exc)[1700]}\n```
        """
        send_discord_message(settings.DISCORD_WEBHOOK, error_message, 'Interceptor')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
        content={"message": 'A server error occurred.', 'trace_id': request_id}
    )

app.include_router(user_router)
app.include_router(auth_router)