import logging
import os
from typing import Optional

from pydantic import BaseSettings, validator

logger = logging.getLogger(__name__)


class DSNSettings(BaseSettings):
    HOST: str = '127.0.0.1'
    PORT: int = 15432
    DBNAME: str = 'movies_database'
    PASSWORD: str = 'user1234'
    USER: str = 'django_user'
    OPTIONS: str = '-c search_path=content'
    DSN: dict

    @validator('DSN', pre=True)
    def build_dsn(cls, v, values) -> dict:
        if v:
            return v
        return {
            'user': values['USER'],
            'password': values['PASSWORD'],
            'host': values['HOST'],
            'port': values['PORT'],
            'dbname': values['DBNAME'],
            'options': values['OPTIONS'],
        }

    class Config:
        env_prefix = 'DB_'
        env_file = '.env'


class PostgresSettings(DSNSettings):
    DSN: dict = None


class ETLSettings(BaseSettings):
    CHUNK_SIZE: int = 100
    LIMIT_READ_RECORD_DB: Optional[int]
    STATE_FIELD: str = 'updated_at'
    STATE_FILE_PATH: Optional[str]

    class Config:
        env_prefix = 'ETL_'
        env_file = '.env'


class ElasticSearchSettings(BaseSettings):
    HOST: str = 'http://elasticsearch'
    PORT: int = 9200
    FILM_WORKS_INDEX_NAME: str = 'movies'
    PERSONS_INDEX_NAME: str = 'persons'
    GENRES_INDEX_NAME: str = 'genres'
    INDEX_SCHEMA_PATH: str = os.path.dirname(__file__)
    INDEX_SCHEMA_FILE_SUFFIX: str = '_index_schema.json'

    class Config:
        env_prefix = 'ES_'
        env_file = '.env'


class BackoffSettings(BaseSettings):
    FETCH_DELAY: Optional[float]
    MAX_ATTEMPT: Optional[int]

    class Config:
        env_prefix = 'BACKOFF_'
        env_file = '.env'


class AppSettings(BaseSettings):
    SLEEP_TIMEOUT: Optional[float]

    class Config:
        env_prefix = 'APP_'
        env_file = '.env'


class RedisSettings(BaseSettings):
    HOST: str = 'etl-redis'
    PORT: str = 6379

    class Config:
        env_prefix = 'ETL_REDIS_'
        env_file = '.env'


class CommonSettings(BaseSettings):
    DEBUG: bool = False
    LOG_LEVEL: str = 'INFO'
    DB: PostgresSettings = PostgresSettings()
    ES: ElasticSearchSettings = ElasticSearchSettings()
    ETL: ETLSettings = ETLSettings()
    BACKOFF: BackoffSettings = BackoffSettings()
    APP: AppSettings = AppSettings()
    REDIS: RedisSettings = RedisSettings()
