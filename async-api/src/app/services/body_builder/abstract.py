from abc import ABC, abstractmethod
from typing import Any

from app.api.v1.api_schemas import Params


class SearchBodyBuilder(ABC):
    @abstractmethod
    async def build_request_body(self, params: Params, index: str) -> Any:
        """
        Метод строит тело запроса из параметров выданных пользователем.
        @param params: pydantic модель с параметрами запроса.
        @param index: наименование индекса где будет проводиться запрос
        @return: тело запроса учитывающее параметры
        """
