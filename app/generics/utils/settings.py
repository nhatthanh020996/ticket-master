from typing import Any, Dict, List
import json
import redis

from pydantic import BaseModel
from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_PASSWORD_PLAIN: str
    DB_NAME: str

    REP_DB_HOST: str
    REP_DB_PORT: int
    REP_DB_USER: str
    REP_DB_PASSWORD: str
    REP_DB_PASSWORD_PLAIN: str

    DATABASE_URI: PostgresDsn | None = None
    REP_DATABASE_URI: PostgresDsn | None = None
    ENVIRONMENT: str
    
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
    
    SYNC_DATABASE_URI: PostgresDsn | None = None
    @validator('SYNC_DATABASE_URI', pre=True)
    def assemble_sync_db_connection(
        cls, value: str | None, values: Dict[str, Any],  # noqa: N805, WPS110
    ) -> str:
        if isinstance(value, str):
            return value

        return PostgresDsn.build(
            scheme='postgresql+psycopg2',
            username=values.get('DB_USER'),
            password=values.get('DB_PASSWORD'),
            host=values.get('DB_HOST'),
            port=values.get('DB_PORT'),
            path='{0}'.format(values.get('DB_NAME')),
        )
    
    SEARCH_ENGINE: str
    SEARCH_BUSINESS_INDEX_NAME: str = 'business'
    SEARCH_ADDRESS_INDEX_NAME: str = 'address'

    MONGO_CLIENT: str = 'localhost:27017'
    MONGO_SHARING: str = 'localhost:27017'
    MONGO_SEARCH_DB: str
    MONGO_HOST: str = 'localhost'
    MONGO_PORT: int = 27017
    MONGO_USER: str
    MONGO_PASSWORD: str

    ES_HOST: str
    ES_PORT: int
    ES_USERNAME: str
    ES_PASSWORD: str

    IGNORE_REVIEW_STAGE: bool = False
    FEEDBACK_EXPIRE_AFTER: int = 60 * 24 * 3 #minutes
    SWITCH_GROUP_TO_REVIEW_BEFORE: int = 60 * 12 #minutes
    REVIEW_IMMEDIATELY: bool = True

    ENABLE_DEBUG_SLOW_QUERY: bool = False
    PERSIST_NON_LABEL_GROUPS: bool = True
    PENDING_INPUT: bool = False

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ''
    REDIS_DB: int = 0
    REDIS_MAX_CONN_POOL: int = 10

    REDIS_READY_REVIEW_HIGH_PRIORITY_QUEUE: str = 'dms_ready_review_high_queue'
    REDIS_READY_REVIEW_MEDIUM_PRIORITY_QUEUE: str = 'dms_ready_review_medium_queue'
    REDIS_READY_REVIEW_LOW_PRIORITY_QUEUE: str = 'dms_ready_review_low_queue'

    REDIS_CONFLICT_RESOLVES_PREFIX: str = 'conflict_resolves_for'
    
    RABBIT_HOST: str | None = 'localhost'
    RABBIT_PORT: int | None = '5672'
    RABBIT_USERNAME: str | None = None
    RABBIT_PASSWORD: str | None = None
    
    PROCESSING_DIRECT_EXCHANGE: str = 'processing_direct_exchange'
    PROCESSING_CMS_SYNC_QUEUE: str = 'processing_cms_sync_queue'
    PROCESSING_CMS_SYNC_ROUTING_KEY: str = 'processing.cms.sync.key'

    PROCESSING_ML_OBJECT_DETECTION_QUEUE: str = 'processing_ml_object_detection_queue'
    PROCESSING_ML_OBJECT_DETECTION_ROUTING_KEY: str = 'processing.ml.object_detection.key'
    
    PROCESSING_ML_SIMILARITY_DETECTION_QUEUE: str = 'processing_ml_similarity_detection_queue'
    PROCESSING_ML_SIMILARITY_DETECTION_ROUTING_KEY: str = 'processing.ml.similarity_detection.key'

    ML_DIRECT_EXCHANGE: str = 'ml_direct_exchange'
    ML_PROCESSING_DETECTION_QUEUE: str = 'ml_processing_detection_queue'
    ML_PROCESSING_DETECTION_ROUTING_KEY: str = 'ml.processing.detection.key'
    
    ML_PROCESSING_SIMILARITY_QUEUE: str = 'ml_processing_similarity_queue'
    ML_PROCESSING_SIMILARITY_ROUTING_KEY: str = 'ml.processing.similarity.key'

    KAFKA_BOOTSTRAP_SERVER: str

    KAFKA_ML_OBJECT_DETECTION_TOPIC: str
    KAFKA_ML_SIMILARITY_DETECTION_TOPIC: str
    
    KAFKA_PROCESSING_CMS_SYNC_TOPIC: str
    KAFKA_PROCESSING_OBJECT_DETECTION_TOPIC: str
    KAFKA_PROCESSING_SIMI_DETECTION_TOPIC: str
    
    KAFKA_SYNC_GROUP_CONSUMER: str = 'processing.cms.sync'
    KAFKA_OD_GROUP_CONSUMER: str = 'processing.ml.object.detection'
    KAFKA_SIM_GROUP_CONSUMER: str = 'processing.ml.similarity.detection'
    
    KAFKA_SASL: bool = True
    KAFKA_USERNAME: str = None
    KAFKA_PASSWORD: str = None

    LOGGING_LEVEL: str
    LOGGING_HOST: str
    LOGGING_PORT: str

    ENABLE_ALERT_NOTIFICATION: bool
    DISCORD_WEBHOOK: str
    CMS_DOMAIN: str

    class Config:
        env_file = ".env"
        extra = 'allow'



class ApplicationSettings(BaseSettings):
    AUTHJWT_SECRET_KEY: str
    AUTHJWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 6 * 60
    AUTHJWT_ALGORITHM: str = 'HS256'

    class Config:
        env_file = ".env"
        extra = 'allow'


class AppConfigs:
    redis_key = 'app_configs'
    
    class Schema(BaseModel):
        inputter_max_working_minutes_per_group: float = 0.8
        inputter_min_working_hours_per_day: float = 3.0

    def __init__(self, redis_url):
        pool = redis.ConnectionPool.from_url(redis_url)
        self.redis_connection = redis.Redis(connection_pool=pool)
        configs = self.redis_connection.get(self.redis_key)
        if configs is None:
            default_configs = self.Schema()
            self.redis_connection.set(self.redis_key, json.dumps(default_configs.model_dump()))
        
    def __getattr__(self, name: str) -> Any:
        app_configs = json.loads(self.redis_connection.get(self.redis_key))
        configs = self.Schema.model_validate(app_configs)
        return getattr(configs, name)


settings = Settings()
app_settings = ApplicationSettings()
app_configs = AppConfigs(f'redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}')
