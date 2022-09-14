from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union

from app.models.base import ORJSONModel


class Cache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[ORJSONModel]:
        """
        Метод получает данные из кеша.
        @param key: ключ по которому получаем данные.
        @return: кешированные данные по запросу.
        """

    @abstractmethod
    async def set(self, key: str, data: Union[Tuple[list, int], str]) -> None:
        """
        Метод кеширует данные.
        @param key: ключ по которому получаем данные.
        @param data: данные для кеширования.
        @return: None
        """
