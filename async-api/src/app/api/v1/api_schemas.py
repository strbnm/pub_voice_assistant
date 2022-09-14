from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.base import BaseFilmworkModel, BaseItemModel, ORJSONModel


class APIFilmworkDetail(BaseFilmworkModel):
    """Schema describe detailed information about filmwork"""

    description: Optional[str] = Field(
        None, title='Содержание фильма', description='Краткое содержание фильма'
    )
    description_ru: Optional[str] = Field(
        None,
        title='Содержание фильма на русском языке',
        description='Краткое содержание фильма на русском языке',
    )
    release_date: date = Field(None, title='Дата релиза', description='Дата релиза фильма')
    runtime_mins: int = Field(
        ..., title='Продолжительность фильма', description='Продолжительность фильма в минутах'
    )
    genre: Optional[list[BaseItemModel]] = Field(None, title='Жанр', description='Жанр фильма')
    actors: Optional[list[BaseItemModel]] = Field(
        None, title='Актёры', description='Список актёров'
    )
    writers: Optional[list[BaseItemModel]] = Field(
        None, title='Сценаристы', description='Список сценаристов'
    )
    directors: Optional[list[BaseItemModel]] = Field(
        None, title='Режиссёры', description='Список режиссёров'
    )
    actors_names: Optional[list[str]] = Field(
        None, title='Актёры', description='Список имён актёров'
    )
    writers_names: Optional[list[str]] = Field(
        None, title='Сценаристы', description='Список имён сценаристов'
    )
    directors_names: Optional[list[str]] = Field(
        None, title='Режиссёры', description='Список имён режиссёров'
    )
    actors_names_ru: Optional[list[str]] = Field(
        None, title='Актёры', description='Список имён актёров на русском языке'
    )
    writers_names_ru: Optional[list[str]] = Field(
        None, title='Сценаристы', description='Список имён сценаристов на русском языке'
    )
    directors_names_ru: Optional[list[str]] = Field(
        None, title='Режиссёры', description='Список имён режиссёров на русском языке'
    )


class APIBaseItemsList(ORJSONModel):
    total: int = Field(..., title='Total', description='Количество найденных объектов')
    page: Optional[int] = Field(None, title='UUID', description='Текущая страница результатов')
    count: int = Field(
        ..., title='UUID', description='Количество объектов на текущей странице'
    )


class Filter(ORJSONModel):
    genre: Optional[str] = Field(
        None, title='Genre UUID', description='Уникальный идентификатор жанра'
    )
    person: Optional[str] = Field(
        None, title='Person UUID', description='Уникальный идентификатор персоны'
    )


class APIFilmworksList(APIBaseItemsList):
    items: list[BaseFilmworkModel]


class APIFilmworkShort(BaseFilmworkModel):
    """Schema describe short information about filmwork.
    Used in filmwork search results by person, genre, etc."""


class APIGenreDetail(ORJSONModel):
    """Schema describe detailed information about genre"""

    uuid: UUID = Field(..., title='UUID', description='Уникальный идентификатор жанра')
    name: str = Field(..., title='Имя жанра', description='Наименование жанра')
    description: Optional[str] = Field(
        None, title='Описание жанра', description='Краткое описание жанра'
    )


class APIGenresList(APIBaseItemsList):
    items: list[APIGenreDetail]


class APIPersonDetail(ORJSONModel):
    uuid: UUID = Field(..., title='UUID', description='Уникальный идентификатор')
    full_name: str = Field(
        ..., title='Имя персоны', description='Полное имя актера, сценариста или режиссёра'
    )
    full_name_ru: str = Field(
        ...,
        title='Имя персоны на русском языке',
        description='Полное имя актера, сценариста или режиссёра на русском языке',
    )
    roles: list[str] = Field(
        ..., title='Роль', description='Роль в фильме: актёр, сценарист или режиссёр'
    )
    film_ids: list[UUID] = Field(
        ..., title='Фильмы', description='Перечень фильмов, в которых принимал участие'
    )


class KWARGS(ORJSONModel):
    @classmethod
    def get_kwargs(cls):
        return cls().dict(exclude_none=True)


class GetFilmsKWARGS(KWARGS):
    summary = 'Получение списка кинопроизведений.'
    description = 'Получение списка кинопроизведений с учетом пагинации и фильтров.'
    response_description = 'Список с Названиями и рейтингами фильмов.'


class SearchFilmsKWARGS(KWARGS):
    summary = 'Поиск кинопроизведений.'
    description = 'Полнотекстовый поиск по кинопроизведениям.'
    response_description = 'Название и рейтинг фильма.'


class GetFilmByIdKWARGS(KWARGS):
    summary = 'Получение информацию по фильму.'
    description = 'Получение полной информации о фильме по UUID.'
    response_description = 'Полная информация по фильму.'


class GetGenresKWARGS(KWARGS):
    summary = 'Получение списка Жанров.'
    description = 'Получение списка Жанров с учетом пагинации.'
    response_description = 'Список с Названиями и описанием жанров.'


class GetGenreByIdKWARGS(KWARGS):
    summary = 'Получение информацию по Жанру.'
    description = 'Получение информации о жанре по UUID.'
    response_description = 'Полная информация по фильму.'


class GetFilmsByPersonKWARGS(KWARGS):
    summary = 'Получение списка кинопроизведений Персоны'
    description = 'Получение списка кинопроизведений в которых принимала участие персона с указанным UUID.'
    response_description = 'Список с названием и рейтингом фильмов.'


class SearchPersonsKWARGS(KWARGS):
    summary = 'Поиск по персонам'
    description = 'Полнотекстовый поиск по Персонам'
    response_description = (
        'Список из Имен персон, их роли в фильмах и списками из UUID фильмов с их участием'
    )


class GetPersonByIdKWARGS(KWARGS):
    summary = 'Получение информацию по персоне'
    description = 'Получение полной информации о персоне по UUID'
    response_description = (
        'Имя персоны, его роли в кино и список из UUID фильмов с его участием'
    )


class APIPersonsList(APIBaseItemsList):
    items: list[APIPersonDetail]


class ExceptionMessages(Enum):
    OBJECT_NOT_FOUND = 'No objects were found matching the parameters.'
    SEARCH_SERVICE_NOT_AVAILABLE = 'Search service not available.'
    PAGE_OUT_OF_RANGE = 'Page number out of range. Max page is {}'


class Pagination(ORJSONModel):
    offset: int
    limit: int
    page: int

    def __init__(self, page, limit):
        offset = (page - 1) * limit
        super().__init__(offset=offset, limit=limit, page=page)


class Params(ORJSONModel):
    pagination: Pagination
    sort_field: str = '_score'
    query: Optional[str]
    filter_query: Filter = Filter()
    is_subscriber: Optional[bool] = None
