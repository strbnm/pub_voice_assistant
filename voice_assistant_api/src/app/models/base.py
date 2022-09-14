from typing import Optional
from uuid import UUID

import orjson
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class ORJSONModel(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseItemModel(ORJSONModel):
    uuid: UUID = Field(..., description='Уникальный идентификатор')
    name: str = Field(..., description='Полное имя персоны или наименование жанра')


class BaseFilmModel(ORJSONModel):
    uuid: UUID = Field(..., description='Уникальный идентификатор фильма')
    title: str = Field(..., description='Заголовок фильма или сериала')
    title_ru: str = Field(..., description='Заголовок фильма или сериала на русском языке')
    imdb_rating: Optional[float] = Field(
        None, description='Рейтинг фильма по версии IMDb', ge=0, le=10
    )
