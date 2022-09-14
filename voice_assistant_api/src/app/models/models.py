from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import Field, AnyUrl

from app.models.base import BaseFilmModel, BaseItemModel, ORJSONModel


class APIBaseItemsList(ORJSONModel):
    """Базовая модель списка фильмов"""

    total: int = Field(..., description='Количество найденных объектов')
    page: Optional[int] = Field(None, description='Текущая страница результатов')
    count: int = Field(..., description='Количество объектов на текущей странице')


class APIFilmsList(APIBaseItemsList):
    """Модель списка фильмов"""

    items: list[BaseFilmModel]


class APIFilmDetail(BaseFilmModel):
    """Модель детальной информации о фильме"""

    description: Optional[str] = Field(None, description='Краткое содержание фильма')
    description_ru: Optional[str] = Field(
        None, description='Краткое содержание фильма на русском языке'
    )
    genre: list[BaseItemModel] = Field(default_factory=list, description='Жанр фильма')
    actors: list[BaseItemModel] = Field(default_factory=list, description='Список актёров')
    writers: list[BaseItemModel] = Field(
        default_factory=list, description='Список сценаристов'
    )
    directors: list[BaseItemModel] = Field(
        default_factory=list, description='Список режиссёров'
    )
    actors_names: list[str] = Field(default_factory=list, description='Список имён актёров')
    writers_names: list[str] = Field(
        default_factory=list, description='Список имён сценаристов'
    )
    directors_names: list[str] = Field(
        default_factory=list, description='Список имён режиссёров'
    )
    actors_names_ru: list[str] = Field(
        default_factory=list, description='Список имён актёров на русском языке'
    )
    writers_names_ru: list[str] = Field(
        default_factory=list, description='Список имён сценаристов на русском языке'
    )
    directors_names_ru: list[str] = Field(
        default_factory=list, description='Список имён режиссёров на русском языке'
    )
    imdb_image: Optional[AnyUrl] = Field(None, description='URL изображения постера фильма')
    runtime_mins: Optional[int] = Field(None, description='Продолжительность фильма в минутах')
    release_date: Optional[date] = Field(None, description='Дата релиза фильма')
    imdb_titleid: Optional[str] = Field(
        None, description='Уникальный идентификатор фильма в IMDB'
    )


class APIPersonDetail(ORJSONModel):
    """Модель детальной информации о персоне"""

    uuid: UUID = Field(..., description='Уникальный идентификатор')
    full_name: str = Field(..., description='Полное имя актера, сценариста или режиссёра')
    full_name_ru: str = Field(
        ..., description='Полное имя актера, сценариста или режиссёра на русском языке'
    )
    roles: list[str] = Field(..., description='Роль в фильме: актёр, сценарист или режиссёр')
    film_ids: list[UUID] = Field(
        ..., title='Фильмы', description='Перечень фильмов, в которых принимал участие'
    )


class APIPersonsList(APIBaseItemsList):
    """Модель списка персон"""

    items: list[APIPersonDetail]
