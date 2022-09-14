from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.settings.config import settings

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS.DSN)


def init_limiter(app: Flask):
    app.config['RATELIMIT_DEFAULT'] = settings.LIMITER.RATELIMIT_DEFAULT
    app.config['RATELIMIT_HEADERS_ENABLED'] = settings.LIMITER.RATELIMIT_HEADERS_ENABLED
    app.config['RATELIMIT_HEADER_RETRY_AFTER_VALUE'] = 'delta-seconds'
    app.config['RATELIMIT_IN_MEMORY_FALLBACK_ENABLED'] = True
    app.config['RATELIMIT_KEY_PREFIX'] = 'auth_ratelimit_'
    limiter.init_app(app)
