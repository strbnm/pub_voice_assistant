from abc import ABC, abstractmethod
from typing import Optional

from app.api.v1.api_schemas import Params

from app.models.base import ORJSONModel


class Controller(ABC):
    """
    Абстрактный класс контроллер, обеспечивает связь между
    функциями ендпоинтов и сервисами необходимыми сервисами.
    """

    @abstractmethod
    async def get_by_id(self, object_id: str) -> ORJSONModel:
        """
        Метод для получения объекта по его id.
        @param object_id: uuid необходимого объекта.
        @return: искомый объект сериализованый в pydantic модели
        """

    @abstractmethod
    async def get_by_params(self, params: Params) -> (Optional[list[ORJSONModel]], int):
        """
        Метод отвечающий за поиск объектов по параметрам.
        @param params: параметры запроса.
        @return: список из сериализованых объектов и общее их количество.
        """

    @abstractmethod
    def get_cache_key(self, params: Params) -> str:
        """
        метод генерирует строку-ключ для кэша.
        @param params: параметры запроса.
        @return: строка-ключ для использования в кэше.
        """
