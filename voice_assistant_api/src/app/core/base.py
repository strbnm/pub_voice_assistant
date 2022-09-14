import logging
from typing import Optional

from pydantic import BaseSettings, Field, AnyUrl

logger = logging.getLogger(__name__)


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
    PROJECT_NAME: str = Field('Voice Assistant Backend', description='Имя проекта')
    PER_PAGE: int = Field(
        5, description='Количество результатов в ответе голосового помощника'
    )

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
    ACCESS_TOKEN: str = Field(..., description='JWT-токен доступа к ресурсам')

    class Config:
        env_prefix = 'AUTH_'


class RequestSettings(BaseSettings):
    ASYNC_API_URL: AnyUrl = Field(..., description='Строка url к корневому эндпоинту AsyncAPI')
    AUTH_API_URL: AnyUrl = Field(..., description='Строка url к корневому эндпоинту AuthAPI')

    class Config:
        env_prefix = 'REQUEST_'


class MongoDBSettings(BaseSettings):
    DB_USER: str = Field('', description='Имя пользователя')
    DB_PASS: str = Field('', description='Пароль пользователя')
    DB_HOSTS: str = Field('', description='Список хостов Mongos')
    DB_RS: str = Field('', description='Имя реплики')
    DB_NAME: str = Field('', description='Имя базы данных MongoDB')
    CACERT: str = Field('', description='Путь к файлу сертификата SSL')

    class Config:
        env_prefix = 'MONGO_'
        env_file = '.env'


class CommonSettings(BaseSettings):
    LOG_LEVEL: str = Field('INFO', description='Уровень логирования сервисов приложения')
    APP: APPSettings = APPSettings()
    CACHE: CacheSettings = CacheSettings()
    REDIS: RedisSettings = RedisSettings()
    BACKOFF: BackoffSettings = BackoffSettings()
    JAEGER: TracingSettings = TracingSettings()
    AUTH: AuthSettings = AuthSettings()
    REQUEST: RequestSettings = RequestSettings()
    MONGO: MongoDBSettings = MongoDBSettings()
