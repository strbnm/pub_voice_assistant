from enum import Enum

from authlib.integrations.flask_client import OAuth
from flask import Flask

from app.redis_service import redis_connection
from app.settings.config import settings


class OAuthTwoEnum(str, Enum):
    GOOGLE = 'google'
    YANDEX = 'yandex'


oauth = OAuth()


def compliance_fix(client, user_data):
    return {
        'sub': user_data['id'],
        'name': user_data['display_name'],
        'email': user_data['default_email'],
    }


oauth.register(
    name=OAuthTwoEnum.GOOGLE.value,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)
oauth.register(
    name=OAuthTwoEnum.YANDEX.value,
    authorize_params={'response_type': 'code'},
    userinfo_endpoint=settings.OAUTH.YANDEX.USERINFO_ENDPOINT,
    token_placement='header',
    userinfo_compliance_fix=compliance_fix,
)


def init_oauth(app: Flask):
    app.config['GOOGLE_CLIENT_ID'] = settings.OAUTH.GOOGLE.CLIENT_ID
    app.config['GOOGLE_CLIENT_SECRET'] = settings.OAUTH.GOOGLE.CLIENT_SECRET
    app.config['YANDEX_CLIENT_ID'] = settings.OAUTH.YANDEX.CLIENT_ID
    app.config['YANDEX_CLIENT_SECRET'] = settings.OAUTH.YANDEX.CLIENT_SECRET
    app.config['YANDEX_API_BASE_URL'] = settings.OAUTH.YANDEX.API_BASE_URL
    app.config['YANDEX_ACCESS_TOKEN_URL'] = settings.OAUTH.YANDEX.ACCESS_TOKEN_URL
    app.config['YANDEX_AUTHORIZE_URL'] = settings.OAUTH.YANDEX.AUTHORIZE_URL

    oauth.init_app(app, cache=redis_connection)
