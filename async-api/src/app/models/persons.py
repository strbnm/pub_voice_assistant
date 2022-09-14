from uuid import UUID

from pydantic import Field

from app.models.base import BaseFilmworkModel, ORJSONModel


class ESPerson(ORJSONModel):
    """Schema describe Person instance doc,
    which will get from persons index ElasticSearch"""

    uuid: UUID = Field(title='UUID', description='Уникальный идентификатор')
    full_name: str = Field(
        title='Имя персоны', description='Полное имя актера, сценариста или режисёра'
    )
    full_name_ru: str = Field(
        ...,
        title='Имя персоны на русском языке',
        description='Полное имя актера, сценариста или режиссёра на русском языке',
    )
    roles: list[str] = Field(
        title='Роль', description='Роль в фильме: актёр, сценарист или режисёр'
    )
    film_ids: list[UUID] = Field(
        title='Фильмы', description='Перечень фильмов, в которых принимал участие'
    )


class ESFilmworkPerson(BaseFilmworkModel):
    """Schema describe Film instance doc by person,
    which will get from movies index ElasticSearch"""


class ESListPersons(ORJSONModel):
    """Schema describe list Person instance doc,
    which will get from persons index ElasticSearch"""

    items: list[ESPerson]


class ESListFilmPersonSchema(ORJSONModel):
    """Schema describe list Film instance doc by person,
    which will get from movies index ElasticSearch"""

    items: list[ESFilmworkPerson]
