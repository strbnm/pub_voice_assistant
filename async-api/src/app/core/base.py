import logging
from typing import Optional

from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)


class ElasticSearchSettings(BaseSettings):
    HOST: str = Field('127.0.0.1', description='Адрес хоста ElasticSearch')
    PORT: int = Field(9200, description='Порт хоста ElasticSearch')
    DEFAULT_PAGE: int = Field(1, description='Номер страницы по умолчанию')
    DEFAULT_PAGE_SIZE: int = Field(
        10, description='Количество результатов на странице по умолчанию'
    )

    class Config:
        env_prefix = 'ES_'
        env_file = '.env'


class RedisSettings(BaseSettings):
    HOST: str = Field('127.0.0.1', description='Адрес хоста DB Redis')
    PORT: str = Field(6379, description='Порт хоста DB Redis')

    class Config:
        env_prefix = 'REDIS_'
        env_file = '.env'


class CacheSettings(BaseSettings):
    TTL: Optional[int] = Field(
        300, description='Время истечения срока действия ключа в секундах'
    )

    class Config:
        env_prefix = 'CACHE_'
        env_file = '.env'


class APPSettings(BaseSettings):
    PROJECT_NAME: str = Field('movies', description='Имя проекта')

    class Config:
        env_prefix = 'APP_'
        env_file = '.env'


class BackoffSettings(BaseSettings):
    RETRIES: int = Field(
        5, description='количество повторных попыток подключения к внешним сервисам'
    )
    TTS: int = Field(2, description='Время ожидания до следующей попытки в секундах')
    MAX_TIME: int = Field(120, description='Максимальное время ожидания для попытки')

    class Config:
        env_prefix = 'BACKOFF_'
        env_file = '.env'


class TracingSettings(BaseSettings):
    AGENT_HOST_NAME: str = Field('127.0.0.1', description='адрес хоста агента Jaeger')
    AGENT_PORT: int = Field(6831, description='номер порта агента Jaeger')
    ENABLED: bool = Field(False, description='Флаг влк./откл. трассировки')

    class Config:
        env_prefix = 'JAEGER_'


class AuthSettings(BaseSettings):
    SECRET_KEY: str = Field('super_big_secret', description='Секретный ключ JWT')
    ALGORITHM: str = Field('HS256', description='Алгоритм шифрования')

    class Config:
        env_prefix = 'AUTH_'


class CommonSettings(BaseSettings):
    LOG_LEVEL: str = Field('INFO', description='Уровень логирования сервисов приложения')
    APP: APPSettings = APPSettings()
    ES: ElasticSearchSettings = ElasticSearchSettings()
    CACHE: CacheSettings = CacheSettings()
    REDIS: RedisSettings = RedisSettings()
    BACKOFF: BackoffSettings = BackoffSettings()
    JAEGER: TracingSettings = TracingSettings()
    AUTH: AuthSettings = AuthSettings()
