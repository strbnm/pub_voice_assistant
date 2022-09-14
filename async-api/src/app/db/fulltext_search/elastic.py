from http import HTTPStatus
from math import ceil

from app.api.v1.api_schemas import ExceptionMessages, Pagination
from app.db.fulltext_search.abstract import FullTextSearchService
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError
from fastapi import HTTPException

from app.models.base import ESSearchAnswer, ORJSONModel


class ESService(FullTextSearchService):
    def __init__(self, service: AsyncElasticsearch):
        self.service = service

    async def get_object_by_id(
        self, index: str, object_id: str, model: ORJSONModel.__class__
    ) -> ORJSONModel:
        try:
            doc = await self.service.get(index=index, id=object_id)
        except NotFoundError:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=ExceptionMessages.OBJECT_NOT_FOUND.value,
            )
        except ConnectionError:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail=ExceptionMessages.SEARCH_SERVICE_NOT_AVAILABLE.value,
            )
        return model(**doc['_source'])

    async def search(self, index: str, pagination: Pagination, body: dict) -> ESSearchAnswer:
        try:
            docs = await self.service.search(
                index=index, body=body, from_=pagination.offset, size=pagination.limit
            )
        except NotFoundError:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=ExceptionMessages.OBJECT_NOT_FOUND.value,
            )
        except ConnectionError:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail=ExceptionMessages.SEARCH_SERVICE_NOT_AVAILABLE.value,
            )
        res = ESSearchAnswer(**docs)
        max_page = ceil(res.hits.total.value / pagination.limit)
        if not res.hits.hits:
            if max_page and pagination.page > max_page:
                raise HTTPException(
                    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                    detail=ExceptionMessages.PAGE_OUT_OF_RANGE.value.format(max_page),
                )
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=ExceptionMessages.OBJECT_NOT_FOUND.value,
            )
        return res
