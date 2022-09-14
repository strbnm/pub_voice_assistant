import logging
from functools import wraps

from flask import Flask
from flask_caching import Cache
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from app.settings.config import settings

cache = Cache()
logger = logging.getLogger(__name__)


def cached(func):
    """Декоратор для кеширования в Redis результатов запросов пользователя
    при валидном access-токене, для исключения повторного обращения в базу данных.
    В качестве префикса ключа используется user_id, извлеченный из поля sub payload access-токена.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return cache.cached(key_prefix=get_jwt()['sub'])(func)(*args, **kwargs)

    return wrapper


def init_cache(app: Flask):
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = settings.REDIS.DSN
    app.config['CACHE_DEFAULT_TIMEOUT'] = settings.CACHE.TTL
    logger.debug('Строка подключения к REDIS: %s', settings.REDIS.DSN)
    cache.init_app(app)
