from abc import ABC
from enum import Enum
from http import HTTPStatus


class APIError(Exception, ABC):
    """Abstract class for all custom API Exceptions"""

    code: HTTPStatus
    description: str

    def __init__(self, description=None, *args):
        self.description = description or self.description
        self.description.format(*args)
        super().__init__()


class APIAuthError(APIError):
    """Custom Authentication Error Class."""

    code = HTTPStatus.FORBIDDEN
    description = 'Authentication Error'


class APIInternalError(APIError):
    """Custom Internal Server Error Class."""

    code = HTTPStatus.INTERNAL_SERVER_ERROR
    description = 'Internal Server Error'


class APIConflictError(APIError):
    """Custom Conflict Error Class."""

    code = HTTPStatus.CONFLICT
    description = 'Conflict Error'


class APINotFoundError(APIError):
    """Custom Not Found Error Class."""

    code = HTTPStatus.NOT_FOUND
    description = 'Not Found Error'


class APIBadRequestError(APIError):
    """Custom Bad Request Error Class."""

    code = HTTPStatus.BAD_REQUEST
    description = 'Bad Request Error'


class APIUnauthorizedError(APIError):
    """Custom Unauthorized Error Class."""

    code = HTTPStatus.UNAUTHORIZED
    description = 'Unauthorized Error'
    message = 'Пользователь не авторизован!'


class PaginationError(APIBadRequestError):
    description = 'Pagination data is not valid.'


class AccountsServiceError(APIUnauthorizedError):
    pass


class AuthorizationError(APIUnauthorizedError):
    pass


class BaseTokenStorageError(APIUnauthorizedError):
    pass


class TokenStorageError(BaseTokenStorageError):
    pass


class InvalidTokenError(BaseTokenStorageError):
    pass


class OAuthServiceError(APIError):
    pass


class ErrorsMessages(Enum):
    EMAIL_IS_BUSY = 'Пользователь с такой электронной почтой уже существует!'
    ROLE_IS_EXIST_TO_USER = 'У пользователя уже есть роль "{}".'
    USER_HAS_NO_ROLE = 'У пользователя уже есть роль "{}".'
    ROLE_IS_EXIST = 'Роль с таким именем уже существует'
    DB_IS_NOT_AVAIBLE = 'Сервис базы данных не доступен.'
    CACHE_IS_NOT_AVAIBLE = 'Сервис кэширования не доступен'
    WRONG_OLD_PASSWORD = 'Неверно указан старый пароль.'
    UNABLE_TO_DELETE_BASE_ROLE_VALUE = 'Невозможно удалить базовую роль.'
    UNABLE_TO_CHANGE_BASE_ROLE_VALUE = 'Невозможно изменить базовую роль.'
    NOTHING_TO_CHANGE = 'Не указаны новые значания ни для одного из полей'
    TOKEN_REVOKED_OR_EXPIRED = 'Пользователь не авторизован!'
    WRONG_TOKEN = 'Недопустимый токен'
    AUTHORIZATION_HEADER = 'Отсутствует или некорректный заголовок авторизации'
    BAD_SIGNATURE = 'Ссылка для подтверждения недействительна или срок ее действия истек.'
