from uuid import UUID, uuid4

from flask import Request
from flask_jwt_extended import create_access_token, create_refresh_token
from user_agents import parse

from app.database import db, session_scope
from app.errors import (
    AccountsServiceError,
    AuthorizationError,
    InvalidTokenError,
    TokenStorageError,
)
from app.models.history import HistoryUserAuth, PlatformEnum
from app.models.user import User
from app.services.storages import token_storage
from app.utils import traced


class AccountsService:
    def __init__(self, user: User):
        self.user = user

    @traced('AccountsService.login')
    def login(self, request: Request) -> tuple[str, str]:
        """Метод авторизации пользователя

        Сохраняет запись в историю посещений и создает пару токенов для пользователя

        :param request: Объект запроса, содержащий информацию о user-agent и ip-адресе
        :return: Пара токенов (access, refresh) для пользователя
        """
        self.record_login_history(request)
        try:
            access_token, refresh_token = self.get_token_pair()
        except TokenStorageError as err:
            raise AccountsServiceError from err

        return access_token, refresh_token

    @staticmethod
    @traced('AccountsService.logout')
    def logout(access_token_jti: str, user_id: UUID) -> None:
        """Метод выхода пользователя из аккаунта

        Используется при logout пользователя. Вызывает метод сохранения jti access-токена в black list
        и удаления refresh-токен для заданного пользователя из хранилища

        :param access_token_jti: уникальный идентификатор JWT (jti) access-токена
        :param user_id: уникальный идентификатор пользователя
        """
        try:
            token_storage.invalidate_token_pair(access_token_jti, user_id)
        except TokenStorageError as err:
            raise AccountsServiceError from err

    @staticmethod
    @traced('AccountsService.get_authorized_user')
    def get_authorized_user(email: str, password: str) -> User:
        """Статический метод авторизации пользователя по email и паролю

        Проверяет существует ли пользователь с таким адресом электронной почты и совпадение
        пароля пользователя. Случае успеха возвращает объект User для данного пользователя

        :param email: логин (email) пользователя
        :param password: строка пароля
        :return: экземпляр User для текущего пользователя
         """
        user = User.query.filter_by(email=email).one_or_none()
        if not user or not user.check_password(password):
            raise AccountsServiceError

        return user

    @traced('AccountsService.get_token_pair')
    def get_token_pair(self) -> tuple[str, str]:
        """Метод создания пары токенов для текущего пользователя

        Создает пару токенов авторизации и сохраняет refresh-токен в хранилище

        :return: Пара токенов (access, refresh) для пользователя
        """
        access_token = create_access_token(
            identity=self.user,
            additional_claims={
                'is_admin': self.user.is_admin,
                'is_staff': self.user.is_staff,
                'roles': self.user.roles_list,
            },
        )
        refresh_token_jti = str(uuid4())
        refresh_token = create_refresh_token(
            identity=self.user, additional_claims={'jti': refresh_token_jti},
        )
        try:
            token_storage.set_refresh_token(refresh_token_jti, self.user.id)
        except TokenStorageError as err:
            raise AccountsServiceError from err

        return access_token, refresh_token

    @traced('AccountsService.refresh_token_pair')
    def refresh_token_pair(self, refresh_token_jti: str) -> tuple[str, str]:
        """Метод обмена пары токенов на refresh-токен

        Проверяет актуальность переданного refresh-токена (наличие в хранилище) и
        в случае успеха генерирует новую пару токенов пользователя

        :param refresh_token_jti: уникальный идентификатор JWT (jti) refresh-токена
        :return: Пара токенов (access, refresh) для пользователя
        """
        try:
            token_storage.validate_refresh_token(refresh_token_jti, self.user.id)
        except InvalidTokenError as err:
            token_storage.invalidate_current_refresh_token(self.user.id)
            raise AuthorizationError from err

        return self.get_token_pair()

    @traced('AccountsService.record_login_history')
    def record_login_history(self, request: Request) -> None:
        """Метод записи истории авторизации

        Сохраняет в базу данных информацию о времени входа пользователя, пользовательском агенте,
        IP адресе, утройстве и платформе

        :param request: Объект запроса, содержащий информацию о user-agent, ip-адресе и др.
        """
        user_agent = parse(request.user_agent.string)
        platform = PlatformEnum.pc
        if user_agent.is_mobile:
            platform = PlatformEnum.mobile
        elif user_agent.is_tablet:
            platform = PlatformEnum.tablet
        with session_scope():
            history = HistoryUserAuth()
            history.user_id = (self.user.id,)
            history.user_agent = (request.user_agent.string,)
            history.ip_addr = (request.remote_addr,)
            history.device = user_agent.device.family
            history.platform = platform
            db.session.add(history)
