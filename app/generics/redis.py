import redis.asyncio as redis

from .settings import settings


def init_redis_pool() -> redis.Redis:
    pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                                db=settings.REDIS_DB,
                                password=settings.REDIS_PASSWORD,
                                max_connections=settings.REDIS_MAX_CONN_POOL,
                                encoding="utf-8",
                                decode_responses=True)
    
    r = redis.Redis(connection_pool=pool)
    return r

redis_connection = init_redis_pool()
