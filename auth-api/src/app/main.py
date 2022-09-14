from logging.config import dictConfig

from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix

from app.api import init_api
from app.cache import init_cache
from app.cli_service import create_superuser
from app.database import init_db
from app.datastore import init_datastore
from app.jaeger_service import init_tracer
from app.jwt_service import init_jwt
from app.limiter import init_limiter
from app.oauth import init_oauth
from app.settings.config import runtime_settings, settings
from app.settings.logger import LOGGING

dictConfig(LOGGING)


def create_app():
    app = Flask(settings.FLASK_APP)
    app.config['DEBUG'] = settings.DEBUG
    app.config['SECRET_KEY'] = settings.SECURITY.SECRET_KEY
    app.config['BUNDLE_ERRORS'] = True
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
    # Инициализация сервисов
    init_db(app)
    init_datastore(app)
    init_api(app)
    init_jwt(app)
    init_cache(app)
    init_limiter(app)
    init_oauth(app)
    app.app_context().push()
    init_tracer(app)
    app.cli.add_command(create_superuser)

    @app.before_request
    def before_request():
        if settings.TESTING:
            return
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            raise RuntimeError('request id is required')

    return app


if runtime_settings == 'dev':
    app = create_app()

if __name__ == '__main__':
    app.run(host=settings.WSGI.HOST, port=settings.WSGI.PORT)
