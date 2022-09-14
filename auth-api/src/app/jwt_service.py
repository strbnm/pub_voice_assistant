from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager

from app.api import api
from app.errors import TokenStorageError
from app.models.user import User
from app.services.storages import token_storage
from app.settings.config import settings

jwt = JWTManager()
jwt._set_error_handler_callbacks(
    api
)  # https://github.com/vimalloc/flask-jwt-extended/issues/86


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    return User.query.filter_by(id=identity).one_or_none()


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    try:
        return token_storage.validate_access_token(jti)
    except Exception:
        raise TokenStorageError


def init_jwt(app: Flask):
    app.config['JWT_SECRET_KEY'] = settings.JWT.SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        minutes=settings.JWT.ACCESS_TOKEN_EXPIRES
    )
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(
        minutes=settings.JWT.REFRESH_TOKEN_EXPIRES
    )

    jwt.init_app(app)
