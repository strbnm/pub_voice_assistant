from enum import Enum
from typing import Optional

import backoff
from app.api.v1.api_schemas import Params
from app.db.cache.abstract import Cache
from app.db.fulltext_search.abstract import FullTextSearchService
from app.services.body_builder.abstract import SearchBodyBuilder
from app.services.controllers.abstract import Controller

from app.core.backoff_handler import backoff_hdlr, backoff_hdlr_success
from app.core.config import settings
from app.models.base import ORJSONModel


class BaseService(Controller):
    index: str
    model: ORJSONModel.__class__

    def __init__(
        self,
        search_service: FullTextSearchService,
        body_builder: SearchBodyBuilder,
        cache: Cache,
    ):
        self.search_service = search_service
        self.body_builder = body_builder
        self.cache = cache

    @backoff.on_exception(
        wait_gen=backoff.expo,
        max_tries=settings.BACKOFF.RETRIES,
        max_time=settings.BACKOFF.MAX_TIME,
        exception=Exception,
        on_backoff=backoff_hdlr,
        on_success=backoff_hdlr_success,
    )
    async def get_by_id(self, object_id: str) -> Optional[ORJSONModel]:
        cache_key = ':::'.join([self.index, object_id])
        data = await self.cache.get(cache_key)
        obj = self.model.parse_raw(await self.cache.get(cache_key)) if data else None
        if not obj:
            obj = await self.search_service.get_object_by_id(self.index, object_id, self.model)
            await self.cache.set(cache_key, obj.json())
        return obj

    @backoff.on_exception(
        wait_gen=backoff.expo,
        max_tries=settings.BACKOFF.RETRIES,
        max_time=settings.BACKOFF.MAX_TIME,
        exception=Exception,
        on_backoff=backoff_hdlr,
        on_success=backoff_hdlr_success,
    )
    async def get_by_params(self, params: Params) -> (Optional[list[dict]], int):
        objects = await self.cache.get(self.get_cache_key(params))

        if not objects:
            body = await self.body_builder.build_request_body(params, self.index)
            objects = await self.search_service.search(
                index=self.index, pagination=params.pagination, body=body,
            )
            objects = (
                [item.source for item in objects.hits.hits],
                objects.hits.total.value,
            )
            await self.cache.set(self.get_cache_key(params), objects)

        return objects

    def get_cache_key(self, params: Params):
        pass


class IndexEnum(str, Enum):
    MOVIES = 'movies'
    GENRES = 'genres'
    PERSONS = 'persons'
