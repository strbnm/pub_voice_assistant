import http
from functools import wraps
from http import HTTPStatus
from logging import Logger

import requests as requests
from flask import request
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_jwt_extended.exceptions import (
    JWTDecodeError,
    NoAuthorizationError,
    RevokedTokenError,
    WrongTokenError,
)
from flask_restx import abort
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from opentelemetry.trace import SpanKind
from redis.exceptions import ConnectionError
from sqlalchemy.exc import SQLAlchemyError

from app.errors import APIError, ErrorsMessages
from app.jaeger_service import tracer
from app.settings.config import settings


def roles_required(*roles):
    """Пользовательский декоратор, который проверяет JWT, представленный в запросе,
    а также гарантирует, что у JWT есть утверждение, указывающее,
    что этот пользователь обладает всеми указанными ролями.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims['roles']:
                available_roles = set(claims['roles'])
                required_roles = set(roles)
                if required_roles.issubset(available_roles):
                    return fn(*args, **kwargs)
            return abort(http.HTTPStatus.FORBIDDEN, 'Недостаточно прав. Доступ запрещен.')

        return decorator

    return wrapper


def roles_accepted(*roles):
    """Пользовательский декоратор, который проверяет JWT, представленный в запросе,
    а также гарантирует, что у JWT есть утверждение, указывающее,
    что этот пользователь обладает хотя бы одной из указанных ролей.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims['roles']:
                available_roles = set(claims['roles'])
                accepted_roles = set(roles)
                if not available_roles.isdisjoint(accepted_roles):
                    return fn(*args, **kwargs)
            return abort(http.HTTPStatus.FORBIDDEN, 'Недостаточно прав. Доступ запрещен.')

        return decorator

    return wrapper


def error_processing(logger: Logger):
    """
    Пользовательский декоратор обработки ошибок.
    """

    def decorator(view):
        def wrapper(*args, **kwargs):
            try:
                return view(*args, **kwargs)
            except APIError as apierr:
                logger.info(apierr.description)
                abort(
                    code=apierr.code,
                    message=apierr.description,
                    errors=apierr.code.description,
                )
            except SQLAlchemyError as db_error:
                logger.info(ErrorsMessages.DB_IS_NOT_AVAIBLE.value, db_error)
                # *** Тут должны быть действия уведомляющие разработчиков о том что бд не доступна ***
                abort(
                    code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    errors=ErrorsMessages.DB_IS_NOT_AVAIBLE.value,
                    message=HTTPStatus.INTERNAL_SERVER_ERROR.description,
                )
            except ConnectionError as cache_err:
                logger.info(ErrorsMessages.CACHE_IS_NOT_AVAIBLE.value, cache_err)
                # *** Тут должны быть действия уведомляющие разработчиков о том что кэш-сервис не доступен ***
                abort(
                    code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    errors=ErrorsMessages.CACHE_IS_NOT_AVAIBLE.value,
                    message=HTTPStatus.INTERNAL_SERVER_ERROR.description,
                )
            except (ExpiredSignatureError, RevokedTokenError) as token_err:
                logger.info(HTTPStatus.UNAUTHORIZED.description, token_err)
                abort(
                    code=HTTPStatus.UNAUTHORIZED,
                    errors=ErrorsMessages.TOKEN_REVOKED_OR_EXPIRED.value,
                    message=HTTPStatus.UNAUTHORIZED.description,
                )
            except (WrongTokenError, JWTDecodeError) as token_err:
                logger.info(HTTPStatus.UNAUTHORIZED.description, token_err)
                abort(
                    code=HTTPStatus.UNAUTHORIZED,
                    errors=ErrorsMessages.WRONG_TOKEN.value,
                    message=HTTPStatus.UNAUTHORIZED.description,
                )
            except (NoAuthorizationError,) as token_err:
                logger.info(HTTPStatus.UNAUTHORIZED.description, token_err)
                abort(
                    code=HTTPStatus.UNAUTHORIZED,
                    errors=ErrorsMessages.AUTHORIZATION_HEADER.value,
                    message=HTTPStatus.UNAUTHORIZED.description,
                )

            except InvalidSignatureError as unvalid_token_err:
                logger.info(HTTPStatus.FORBIDDEN.description, unvalid_token_err)
                abort(
                    code=HTTPStatus.FORBIDDEN, message=HTTPStatus.FORBIDDEN.description,
                )

        return wrapper

    return decorator


def traced(name: str):
    """Декоратор для выборочной трассировки функций

    :param name: Имя трассировки для визуальной индентификации спана в JAEGER.
    Рекомендуется указывать в формате <Имя класса>.<имя декорируемой функции>
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if not settings.JAEGER.ENABLED:
                return fn(*args, **kwargs)
            with tracer.start_as_current_span(name, kind=SpanKind.CLIENT) as span:
                span.set_attribute('http.request_id', request.headers.get('X-Request-Id'))
                span.set_attributes({'args': args, **kwargs})
                return fn(*args, **kwargs)

        return decorator

    return wrapper


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(secret_key=settings.SECURITY.SECRET_KEY)
    return serializer.dumps(email, salt=settings.SECURITY.PASSWORD_SALT)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(settings.SECURITY.SECRET_KEY)
    try:
        email = serializer.loads(
            token, salt=settings.SECURITY.PASSWORD_SALT, max_age=expiration
        )
    except (SignatureExpired, BadSignature):
        return False
    return email


def send_notification(payload: dict):
    data = {
        'sender': 'auth',
        'template_type': 'welcome_letter',
        'channel': 'email',
        'request_id': request.headers.get('X-Request-Id'),
        'payload': payload,
    }
    response = requests.post(settings.NOTIFICATION_APP_URL, json=data)
    response.raise_for_status()
