from typing import Any, Dict, Optional

from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_PASSWORD_PLAIN: str
    DB_NAME: str
    CONN_POOL_SIZE: Optional[int] = 8

    REP_DB_HOST: str
    REP_DB_PORT: int
    REP_DB_USER: str
    REP_DB_PASSWORD: str
    REP_DB_PASSWORD_PLAIN: str

    DATABASE_URI: PostgresDsn | None = None
    REP_DATABASE_URI: PostgresDsn | None = None
    
    ENVIRONMENT: str
    LOGGING_LEVEL: str
    
    @validator('DATABASE_URI', pre=True)
    def assemble_db_connection(
        cls, value: str | None, values: Dict[str, Any],  # noqa: N805, WPS110
    ) -> str:
        if isinstance(value, str):
            return value

        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=values.get('DB_USER'),
            password=values.get('DB_PASSWORD'),
            host=values.get('DB_HOST'),
            port=values.get('DB_PORT'),
            path='{0}'.format(values.get('DB_NAME')),
        )
    
    @validator('REP_DATABASE_URI', pre=True)
    def assemble_rep_db_connection(
        cls, value: str | None, values: Dict[str, Any],  # noqa: N805, WPS110
    ) -> str:
        if isinstance(value, str):
            return value

        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=values.get('REP_DB_USER'),
            password=values.get('REP_DB_PASSWORD'),
            host=values.get('REP_DB_HOST'),
            port=values.get('REP_DB_PORT'),
            path='{0}'.format(values.get('DB_NAME')),
        )

    ES_HOST: str
    ES_PORT: int
    ES_USERNAME: str
    ES_PASSWORD: str

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ''
    REDIS_DB: int = 0
    REDIS_MAX_CONN_POOL: int = 10

    KAFKA_BOOTSTRAP_SERVER: str
    KAFKA_SASL: bool = True
    KAFKA_USERNAME: str = None
    KAFKA_PASSWORD: str = None

    ENABLE_ALERT_NOTIFICATION: bool
    DISCORD_WEBHOOK: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ENCRYPT_KEY: str


    class Config:
        env_file = ".env"
        extra = 'allow'



settings = Settings()
