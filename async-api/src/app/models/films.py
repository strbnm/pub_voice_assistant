from datetime import date

from pydantic import Field

from app.models.base import BaseFilmworkModel, BaseItemModel, ORJSONModel


class ESFilmwork(BaseFilmworkModel):
    """Schema describe Filmwork instance doc,
    which will get from ElasticSearch"""

    description: str = Field(
        None, title='Содержание фильма', description='Краткое содержание фильма'
    )
    description_ru: str = Field(
        None,
        title='Содержание фильма на русском языке',
        description='Краткое содержание фильма на русском языке',
    )
    release_date: date = Field(None, title='Дата релиза', description='Дата релиза фильма')
    runtime_mins: int = Field(
        ..., title='Продолжительность фильма', description='Продолжительность фильма в минутах'
    )
    genre: list[BaseItemModel] = Field(list(), title='Жанр', description='Жанр фильма')
    actors: list[BaseItemModel] = Field(list(), title='Актёры', description='Список актёров')
    writers: list[BaseItemModel] = Field(
        list(), title='Сценаристы', description='Список сценаристов'
    )
    directors: list[BaseItemModel] = Field(
        list(), title='Режисёры', description='Список режисёров'
    )
    actors_names: list[str] = Field(
        list(), title='Имена актёров', description='Список имён актёров'
    )
    writers_names: list[str] = Field(
        list(), title='Имена сценаристов', description='Список имён сценаристов'
    )
    directors_names: list[str] = Field(
        list(), title='Имена режисёров', description='Список имён режисёров'
    )
    actors_names_ru: list[str] = Field(
        None, title='Актёры', description='Список имён актёров на русском языке'
    )
    writers_names_ru: list[str] = Field(
        None, title='Сценаристы', description='Список имён сценаристов на русском языке'
    )
    directors_names_ru: list[str] = Field(
        None, title='Режиссёры', description='Список имён режиссёров на русском языке'
    )


class ESListFilmworks(ORJSONModel):
    """Schema describe list Filmwork instance doc,
    which will get from ElasticSearch"""

    items: list[ESFilmwork]
