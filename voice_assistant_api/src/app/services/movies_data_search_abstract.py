from abc import ABC, abstractmethod
from typing import Optional

from app.models.base import ORJSONModel


class MoviesDataSearchAbstract(ABC):
    """Абстрактный класс взаимодействия с сервисом AsyncAPI."""

    @abstractmethod
    async def search_films(
        self,
        query_string: str,
        multiple: bool = False,
        page: int = 1,
        per_page: int = 5,
        in_description: bool = False,
    ) -> ORJSONModel:
        """Метод получения фильма или списка фильмов при поиске по наименованию или описанию фильма.

        :param query_string: строка поискового запроса.
        :param multiple: флаг о необходимости возврата списка с пагинацией по страницам. По умолчанию False -
            возвращает наиболее релевантный (имеющий наибольший score) результат поиска.
        :param page: номер страницы, возвращаемой в результатах поиска.
        :param per_page: количество записей на странице.
        :param in_description: флаг поиска в описании (сюжете) фильма
        :return: фильм или список фильмов, сериализованные с помощью модели.
        """
        pass

    @abstractmethod
    async def get_film_detail(self, film_id: str) -> ORJSONModel:
        """Метод получения детальной информации о фильме.

        :param film_id: уникальный идентификатор фильма.
        :return: детальная информация о фильме, сериализованная с помощью модели.
        """
        pass

    @abstractmethod
    async def search_persons(
        self, query_string: str, multiple: bool = False, page: int = 1, per_page: int = 5
    ) -> ORJSONModel:
        """Метод получения списка персоны или списка персон при поиске по имени персоны.

        :param query_string: строка поискового запроса.
        :param multiple: флаг о необходимости возврата списка с пагинацией по страницам. По умолчанию False -
            возвращает наиболее релевантный (имеющий наибольший score) результат поиска.
        :param page: номер страницы, возвращаемой в результатах поиска.
        :param per_page: количество записей на странице.
        :return: персона или список персон, сериализованные с помощью модели.
        """
        pass

    @abstractmethod
    async def get_person_detail(self, person_id: str) -> ORJSONModel:
        """Метод получения детальной информации о персоне.

        :param person_id: уникальный идентификатор персоны.
        :return: детальная информация о персоне, сериализованная с помощью модели.
        """
        pass

    @abstractmethod
    async def get_list_films(
        self, genre: Optional[str] = None, page: int = 1, per_page: int = 5
    ) -> ORJSONModel:
        """Метод получения списка фильмов, отсортированного в порядке убывания рейтинга, с возможностью фильтрации по
        жанру фильма.

        :param genre: жанр фильма для фильтрации по жанру.
        :param page: номер страницы, возвращаемой в результатах поиска.
        :param per_page: количество записей на странице.
        :return: список фильмов, сериализованный с помощью модели.
        """
        pass

    @abstractmethod
    async def get_list_films_by_person(
        self, person_id: str, page: int = 1, per_page: int = 10
    ) -> ORJSONModel:
        """Метод получения списка фильмов c участием персоны.

        :param person_id: уникальный идентификатор персоны.
        :param page: номер страницы, возвращаемой в результатах поиска.
        :param per_page: количество записей на странице.
        :return: список фильмов, сериализованные с помощью модели.
        """
        pass
