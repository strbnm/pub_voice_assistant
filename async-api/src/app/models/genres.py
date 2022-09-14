from typing import Optional

from pydantic import Field

from app.models.base import BaseItemModel, ORJSONModel


class ESGenre(BaseItemModel):
    """Schema describe Genre instance doc,
    which will get from ElasticSearch"""

    description: Optional[str] = Field(
        None, title='Описание жанра', description='Краткое описание жанра'
    )


class ESListGenres(ORJSONModel):
    """Schema describe list Genre instance doc,
    which will get from ElasticSearch"""

    items: list[ESGenre]
