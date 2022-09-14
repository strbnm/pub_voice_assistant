from abc import ABC, abstractmethod

from app.api.v1.api_schemas import Pagination

from app.models.base import ORJSONModel


class FullTextSearchService(ABC):
    @abstractmethod
    async def get_object_by_id(
        self, index: str, object_id: str, model: ORJSONModel.__class__
    ) -> ORJSONModel:
        """
        Метод для получения конкретного объекта по его id.
        @param index: индекс из которого необходимо получить объект.
        @param object_id: uuid объекта.
        @param model: pydantic модель для сериализации ответа от сервиса.
        @return: искомый объект сериализованый с помощью pydantic модели.
        """

    @abstractmethod
    async def search(self, index, pagination: Pagination, body: dict) -> ORJSONModel:
        """
        Метод для поиска объекта по параметрам.
        @param index: индекс из которого необходимо получить объект.
        @param pagination: параметры пагинации
        @param body: тело запроса содержащее в себе параметры поиска.
        @return: сериализованый объект содержащий список
        с объектами удовлетворяющими заданым параметрам.
        """
