from functools import lru_cache
from typing import Optional

from aioredis import Redis
from app.db.cache.abstract import Cache
from app.db.cache.redis import RedisCache
from app.db.fulltext_search.abstract import FullTextSearchService
from app.db.fulltext_search.elastic import ESService
from app.services.body_builder.abstract import SearchBodyBuilder
from app.services.body_builder.film import FilmElasticBodyBuilder
from app.services.body_builder.genre import GenreElasticBodyBuilder
from app.services.body_builder.person import PersonElasticBodyBuilder
from app.services.controllers.film import FilmService
from app.services.controllers.genre import GenreService
from app.services.controllers.person import PersonService
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

es: Optional[AsyncElasticsearch] = None
redis: Optional[Redis] = None


@lru_cache()
def get_cache():
    return RedisCache(redis)


@lru_cache()
def get_full_text_search_service() -> FullTextSearchService:
    return ESService(es)


@lru_cache()
def get_film_body_builder() -> SearchBodyBuilder:
    return FilmElasticBodyBuilder()


@lru_cache()
def get_genre_body_builder() -> SearchBodyBuilder:
    return GenreElasticBodyBuilder()


@lru_cache()
def get_person_body_builder() -> SearchBodyBuilder:
    return PersonElasticBodyBuilder()


@lru_cache()
def get_film_service(
    elastic: FullTextSearchService = Depends(get_full_text_search_service),
    body_builder: SearchBodyBuilder = Depends(get_film_body_builder),
    cache: Cache = Depends(get_cache),
) -> FilmService:
    return FilmService(elastic, body_builder, cache)


@lru_cache()
def get_genre_service(
    elastic: FullTextSearchService = Depends(get_full_text_search_service),
    body_builder: SearchBodyBuilder = Depends(get_genre_body_builder),
    cache: Cache = Depends(get_cache),
) -> GenreService:
    return GenreService(elastic, body_builder, cache)


@lru_cache()
def get_person_service(
    elastic: FullTextSearchService = Depends(get_full_text_search_service),
    body_builder: SearchBodyBuilder = Depends(get_person_body_builder),
    cache: Cache = Depends(get_cache),
) -> PersonService:
    return PersonService(elastic, body_builder, cache)
