from abc import ABC, abstractmethod
from datetime import timedelta
from uuid import UUID

from redis.client import Pipeline, StrictRedis

from app.errors import InvalidTokenError
from app.redis_service import redis_connection
from app.settings.config import settings
from app.utils import traced


class AbstractTokenStorage(ABC):  # pragma: no cover
    @abstractmethod
    def validate_refresh_token(self, refresh_token: str, user_id: str) -> bool:
        """Метод проверки валидности refresh-токена.

        Запрашивает сохраненный по ключу user_id идентификатор токена, имеющегося в хранилище и
        сравнивает с переданным идентификатором refresh_token. Возвращает результат сравнения.

        :param refresh_token: уникальный идентификатор JWT (jti) refresh-токена
        :param user_id: уникальный идентификатор пользователя
        :return: Возвращает True, если jti refresh-токена есть в хранилище для указанного user_id,
        иначе возвращает False
        """
        pass

    @abstractmethod
    def invalidate_current_refresh_token(self, user_id: str) -> None:
        """Метод аннулирования текущего refresh-токена

        Удаляет из хранилища refresh-токен для заданного пользователя

        :param user_id: уникальный идентификатор пользователя
        """
        pass

    @abstractmethod
    def set_refresh_token(self, new_refresh_token: str, user_id: str) -> None:
        """Метод записи в хранилище нового refresh-токена

        Сохраняет в хранилище по ключу user_id уникальный идентификатор JWT нового refresh-токена

        :param new_refresh_token: уникальный идентификатор JWT (jti) refresh-токена
        :param user_id: уникальный идентификатор пользователя
        """
        pass

    @abstractmethod
    def validate_access_token(self, access_token_jti: str) -> bool:
        """Метод проверки валидности access-токена

        Проверяет наличие access-токена в black list хранилища.

        :param access_token_jti: уникальный идентификатор JWT (jti) access-токена
        :return: Возвращает True, если jti access-токена есть в black list, иначе возвращает False
        """
        pass

    @abstractmethod
    def invalidate_token_pair(self, access_token_jti: str, user_id: str) -> None:
        """Метод аннулирования пары токенов

        Используется при logout пользователя. Сохраняет jti access-токена в black list
        и удаляет refresh-токен для заданного пользователя из хранилища

        :param access_token_jti: уникальный идентификатор JWT (jti) access-токена
        :param user_id: уникальный идентификатор пользователя
        """
        pass


class RedisTokenStorage(AbstractTokenStorage):
    def __init__(self):
        self.redis: StrictRedis = redis_connection

    @traced('RedisTokenStorage.validate_refresh_token')
    def validate_refresh_token(self, refresh_token_jti: str, user_id: UUID) -> None:
        current_refresh_token_jti = self.redis.get(name=str(user_id))

        if not current_refresh_token_jti:
            raise InvalidTokenError

        if current_refresh_token_jti != refresh_token_jti:
            raise InvalidTokenError

        return

    @traced('RedisTokenStorage.invalidate_current_refresh_token')
    def invalidate_current_refresh_token(self, user_id: UUID) -> None:
        self.redis.delete(str(user_id))

    @traced('RedisTokenStorage.set_refresh_token')
    def set_refresh_token(self, token_jti: str, user_id: UUID) -> None:
        self.redis.set(name=str(user_id), value=token_jti)

    @traced('RedisTokenStorage.delete_refresh_token')
    def delete_refresh_token(self, user_id: UUID) -> None:
        self.redis.delete(str(user_id))

    @traced('RedisTokenStorage.validate_access_token')
    def validate_access_token(self, access_token_jti: str) -> bool:
        return bool(self.redis.exists(access_token_jti))

    @traced('RedisTokenStorage.invalidate_token_pair')
    def invalidate_token_pair(self, access_token_jti: str, user_id: UUID) -> None:
        def callback(pipe: Pipeline) -> None:
            pipe.set(
                name=access_token_jti,
                value=str(user_id),
                ex=timedelta(minutes=settings.JWT.ACCESS_TOKEN_EXPIRES),
            )
            pipe.delete(str(user_id))

        self.redis.transaction(func=callback)


token_storage = RedisTokenStorage()
