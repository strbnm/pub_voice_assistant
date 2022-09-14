import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator


class ESBaseSchema(BaseModel):
    uuid: uuid.UUID


class ESFilmworkSchema(ESBaseSchema):
    """Schema describe Filmwork instance doc,
    which will migrate into ElasticSearch"""

    imdb_rating: Optional[float] = None
    genre: Optional[list[dict[str, str]]] = None
    title: str
    description: Optional[str] = None
    actors_names: Optional[list[str]] = None
    writers_names: Optional[list[str]] = None
    directors_names: Optional[list[str]] = None
    actors_names_ru: Optional[list[str]] = None
    writers_names_ru: Optional[list[str]] = None
    directors_names_ru: Optional[list[str]] = None
    actors: Optional[list[dict[str, str]]] = None
    writers: Optional[list[dict[str, str]]] = None
    directors: Optional[list[dict[str, str]]] = None
    subscription_required: bool = True
    description_ru: Optional[str] = None
    title_ru: str
    imdb_titleid: Optional[str] = None
    imdb_image: Optional[str] = None
    release_date: date = datetime.now().strftime('%Y-%m-%d')
    runtime_mins: int = 0

    class Meta:
        LIST_FIELDS = (
            'genre',
            'writers_names',
            'actors_names',
            'directors_names',
            'writers_names_ru',
            'actors_names_ru',
            'directors_names_ru',
            'actors',
            'writers',
            'directors',
        )
        STR_FIELDS = ('description', 'description_ru', 'imdb_titleid', 'imdb_image')

    @validator(*Meta.LIST_FIELDS, pre=True, always=True)
    def set_list_defaults(cls, val):
        return val or []

    @validator(*Meta.STR_FIELDS, pre=True, always=True)
    def set_str_defaults(cls, val):
        return val or None

    @validator('runtime_mins', pre=True, always=True)
    def set_int_defaults(cls, val):
        return val or 0


class ESGenreSchema(ESBaseSchema):
    """Schema describe Genre instance doc,
    which will migrate into ElasticSearch"""

    name: str
    description: Optional[str] = None

    class Meta:
        STR_FIELDS = ('description',)

    @validator(*Meta.STR_FIELDS, pre=True, always=True)
    def set_str_defaults(cls, val):
        return val or None


class ESPersonSchema(ESBaseSchema):
    """Schema describe Person instance doc,
    which will migrate into ElasticSearch"""

    full_name: str
    full_name_ru: str
    roles: Optional[list[str]] = None
    film_ids: Optional[list[uuid.UUID]] = None

    class Meta:
        LIST_FIELDS = (
            'roles',
            'film_ids',
        )

    @validator(*Meta.LIST_FIELDS, pre=True, always=True)
    def set_list_defaults(cls, val):
        return val or []


class DocSchemaEnum(Enum):
    filmwork = ESFilmworkSchema
    person = ESPersonSchema
    genre = ESGenreSchema


class BaseStateSchema(BaseModel):
    es_updated_at: datetime = datetime.now()
    flag_ETL_success: bool = False


class FilmworkStateSchema(BaseStateSchema):
    filmwork_updated_at: Optional[datetime] = datetime.min
    person_updated_at: Optional[datetime] = datetime.min
    genre_updated_at: Optional[datetime] = datetime.min


class GenreStateSchema(BaseStateSchema):
    genre_updated_at: Optional[datetime] = datetime.min


class PersonStateSchema(BaseStateSchema):
    person_updated_at: Optional[datetime] = datetime.min
