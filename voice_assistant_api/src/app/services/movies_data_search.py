import asyncio
import logging
from collections import abc
from typing import Awaitable, Optional

from aiohttp import ClientSession
from fastapi import Depends
from starlette import status

from app.core.config import settings
from app.core.session import get_session
from app.models.models import APIFilmsList, APIFilmDetail, APIPersonsList, APIPersonDetail
from app.services.movies_data_search_abstract import MoviesDataSearchAbstract
from app.utils.text import encode_uri

logger = logging.getLogger(__name__)


class MoviesDataSearch(MoviesDataSearchAbstract):
    def __init__(self, session: ClientSession) -> None:
        self.session = session
        self.url = settings.REQUEST.ASYNC_API_URL
        self.headers = {'Authorization': f'Bearer {settings.AUTH.ACCESS_TOKEN}'}

    async def search_films(
        self,
        query_string: str,
        multiple: bool = False,
        page: int = 1,
        per_page: int = settings.APP.PER_PAGE,
        in_description: bool = False,
    ) -> Optional[APIFilmsList]:
        url = f'{self.url}/film/search?q={query_string}&page={page}'
        if multiple:
            url += f'&limit={per_page}'
        else:
            url += '&limit=1'
        data, resp_status = await self.safe_request(url=url, headers=self.headers)
        if resp_status != status.HTTP_200_OK:
            return
        return APIFilmsList(**data)

    async def get_film_detail(self, film_id: str) -> APIFilmDetail:
        url = f'{self.url}/film/{film_id}'
        data, _ = await self.request(url=url, headers=self.headers)
        return APIFilmDetail(**data)

    async def search_persons(
        self,
        query_string: str,
        multiple: bool = False,
        page: int = 1,
        per_page: int = settings.APP.PER_PAGE,
    ) -> Optional[APIPersonsList]:
        limit = per_page if multiple else 1
        url = f'{self.url}/person/search?q={query_string}&page={page}&limit={limit}'
        data, resp_status = await self.safe_request(url=url, headers=self.headers)
        if resp_status != status.HTTP_200_OK:
            return
        return APIPersonsList(**data)

    async def get_person_detail(self, person_id: str) -> APIPersonDetail:
        url = f'{self.url}/person/{person_id}'
        data, _ = await self.request(url=url, headers=self.headers)
        return APIPersonDetail(**data)

    async def get_list_films(
        self, genre: str = '', page: int = 1, per_page: int = settings.APP.PER_PAGE
    ) -> APIFilmsList:
        if genre:
            url = (
                f'{self.url}/film?sort=-imdb_rating&page={page}&limit={per_page}&genre={genre}'
            )
        else:
            url = f'{self.url}/film?sort=-imdb_rating&page={page}&limit={per_page}'
        data, _ = await self.request(url=url, headers=self.headers)
        return APIFilmsList(**data)

    async def get_list_films_by_person(
        self, person_id: str, page: int = 1, per_page: int = settings.APP.PER_PAGE
    ) -> APIFilmsList:
        url = f'{self.url}/person/{person_id}/film?sort=-imdb_rating&page={page}&limit={per_page}'
        logger.info('url for search films by persons - %s', url)
        data, _ = await self.request(url=url, headers=self.headers)
        logger.info('data - %s', data)
        return APIFilmsList(**data)

    async def safe_request(self, url: str, headers: dict):
        """Метод ограничивающий время ожидания ответа от сервиса AsyncAPI.
        Ожидается что webhook ответит на запрос навыка Яндекс Диалоги в течение 3 секунд.
        https://yandex.ru/blog/dialogs/bolshe-vremeni-na-otvet-time-out-3-sekundy
        ES может отвечать на некоторые запросы существенно дольше, когда запрашиваемое имя персоны
        или наименование фильма отсутствуют в ES. В основном затрагивает запросы поиска по имени персоны
        или названию фильма.

        :param url: строка URL.
        :param headers: словарь со значениями HTTP-заголовков.
        :return: кортеж из тела ответа в JSON и статус ответа.
        """
        response_timeout = 2.5
        background_tasks = set()
        task = asyncio.create_task(self.request(url=url, headers=headers))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=response_timeout)
            return task.result()
        except asyncio.TimeoutError:
            return {}, status.HTTP_408_REQUEST_TIMEOUT

    async def request(self, url: str, headers: dict):
        logger.debug('URL before encode: %s', url)
        url = encode_uri(url)  # avoid cyrillic characters in urls
        logger.debug('URL after encode: %s', url)
        async with self.session.get(url=url, headers=headers) as search_response:
            resp_status = search_response.status
            result = await search_response.json()
            logger.debug('Response from AsyncAPI: %s', result)
            return result, resp_status


async def get_movies_data_search(
    session: Awaitable[ClientSession] = Depends(get_session),
) -> MoviesDataSearch:
    if isinstance(session, abc.Awaitable):
        session = await session
    return MoviesDataSearch(session=session)
