import asyncio
import logging
from asyncio import sleep
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urljoin

import aiohttp
import orjson
import pytest
import uvicorn
from aiocache import Cache
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_streaming_bulk
from functional.settings import CACHE_CONFIG, SERVICE_URL, TEST_SRC_DIR_PATH, test_settings
from httpx import AsyncClient
from jose import jwt
from multidict import CIMultiDictProxy

from app.core.config import settings
from app.core.logger import LOGGING
from app.main import app

assert test_settings.TESTING, 'You must set TESTING=True env for run the tests.'


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session', autouse=True)
def default_page():
    return settings.ES.DEFAULT_PAGE


@pytest.fixture(scope='session', autouse=True)
def default_page_limit():
    return settings.ES.DEFAULT_PAGE_SIZE


@pytest.fixture(scope='session', autouse=True)
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def load_fixture():
    def load(filename):
        with open(Path(TEST_SRC_DIR_PATH) / filename, encoding='utf-8') as file:
            return orjson.loads(file.read())

    return load


@pytest.fixture
async def clear_cache():
    cache = Cache(Cache.REDIS, **CACHE_CONFIG)
    yield cache
    await cache.clear()
    await cache.close()


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=[f'{settings.ES.HOST}:{settings.ES.PORT}'])
    yield client
    await client.indices.delete(
        index='*'
    )  # Удаляем созданные индексы после завершения тестовой сессии
    await client.close()


@pytest.fixture(scope='session')
async def clear_es_client(es_client):
    await es_client.indices.delete(index='*')


@pytest.fixture
async def clear_es_client_func(es_client):
    await es_client.indices.delete(index='*')


@pytest.fixture(scope='session')
def create_es_index(load_fixture, clear_es_client, es_client):
    async def inner(index: str):
        schema_index = load_fixture(f'index_schemes/{index}_index_schema.json')
        await es_client.indices.create(
            index=index,
            settings=schema_index['settings'],
            mappings=schema_index['mappings'],
            ignore=400,
        )
        return await es_client.indices.exists(index=[index])

    return inner


@pytest.fixture
def create_es_index_func(load_fixture, clear_es_client, es_client):
    async def inner(index: str):
        schema_index = load_fixture(f'index_schemes/{index}_index_schema.json')
        await es_client.indices.create(
            index=index,
            settings=schema_index['settings'],
            mappings=schema_index['mappings'],
            ignore=400,
        )
        return await es_client.indices.exists(index=[index])

    return inner


@pytest.fixture(scope='module')
def es_client_load(es_client, create_es_index, load_fixture):
    async def inner(file: str, index: str) -> Tuple[int, int]:
        body_docs = load_fixture(file)
        total_docs = len(body_docs)
        successes = await create_es_index(index=index)
        assert successes is True

        def generate_action():
            for idx, body_doc in enumerate(body_docs):
                action = {'_index': index, '_id': body_doc.get('uuid'), **body_doc}
                yield action

        successes_docs = 0
        async for ok, result in async_streaming_bulk(
            client=es_client, actions=generate_action(),
        ):
            successes_docs += ok
        # Задержка в 2 секунды, чтобы ElasticSearch успел сохранить изменения
        # и обновить индекс перед последующими запросами
        await sleep(2)
        # Возвращаем общее количество документов и количество удачно записанных в ElasticSearch документов
        # чтобы в вызывающей функции или фикстуре можно было проверить, что в индекс записаны все документы
        return total_docs, successes_docs

    return inner


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(make_get_request_aiohttp, make_get_request_httpx):
    """Возвращаем разные функции формирования запроса get в зависимости от значения env RUN_WITH_COVERAGE:
     True:  Hа базе клиента AsyncClient пакета httpx для корректной оценки охвата кода тестами.
                В этом случае используется приложение, запущенное локально в рамках тестовой сессии
                на тестовом сервере UvicornTestServer.
     False: На базе клиента aiohttp.ClientSession если оценка охвата кода тестами не требуется.
                В этом случае запросы get адресуются к серверу uvicorn в контейнере приложения"""

    return (
        make_get_request_httpx if test_settings.RUN_WITH_COVERAGE else make_get_request_aiohttp
    )


@pytest.fixture
def make_get_request_aiohttp(session):
    async def inner(
        endpoint_url: str, params: Optional[dict] = None, headers: Optional[dict] = None
    ) -> HTTPResponse:
        params = params or {}
        headers = headers or {}
        url = urljoin(base=SERVICE_URL, url=endpoint_url)
        async with session.get(url, params=params, headers=headers) as response:
            return HTTPResponse(
                body=(
                    await response.json()
                    if response.headers['Content-Type'] == 'application/json'
                    else await response.text()
                ),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture
def make_get_request_httpx(app_server):
    async def inner(
        endpoint_url: str, params: Optional[dict] = None, headers: Optional[dict] = None
    ) -> HTTPResponse:
        params = params or {}
        headers = headers or {}
        url = urljoin(base=SERVICE_URL, url=endpoint_url)
        async with AsyncClient(app=app, base_url=SERVICE_URL, follow_redirects=True) as ac:
            response = await ac.get(url=url, params=params, headers=headers)
            return HTTPResponse(
                body=(
                    response.json()
                    if response.headers['Content-Type'] == 'application/json'
                    else response.text()
                ),
                headers=response.headers,
                status=response.status_code,
            )

    return inner


@pytest.fixture(scope='function')
def expected(load_fixture, request):
    return load_fixture(request.param)


@pytest.fixture(scope='function')
def expected_not_found(load_fixture):
    return load_fixture('not_found_response.json')


class UvicornTestServer(uvicorn.Server):
    """Uvicorn test server

    Usage:
        @pytest.fixture
        server = UvicornTestServer()
        await server.up()
        yield server
        await server.down()
    """

    def __init__(self, application, host='127.0.0.1', port=8888):
        """Create a Uvicorn test server

        Args:
            application (FastAPI, optional): the FastAPI app. Defaults to main.app.
            host (str, optional): the host ip. Defaults to '127.0.0.1'.
            port (int, optional): the port. Defaults to PORT.
        """
        self._serve_task = None
        self._startup_done = asyncio.Event()
        super().__init__(
            config=uvicorn.Config(
                application, host=host, port=port, log_config=LOGGING, log_level=logging.INFO,
            )
        )

    async def startup(self, sockets: Optional[list] = None) -> None:
        """Override uvicorn startup"""
        await super().startup(sockets=sockets)
        self.config.setup_event_loop()
        self._startup_done.set()

    async def up(self) -> None:
        """Start up server asynchronously"""
        self._serve_task = asyncio.create_task(self.serve())
        await self._startup_done.wait()

    async def down(self) -> None:
        """Shut down server asynchronously"""
        self.should_exit = True
        await self._serve_task


@pytest.fixture(scope='session')
async def app_server():
    """Start server as test fixture and tear down after test"""
    server = UvicornTestServer(app)
    await server.up()
    yield server
    await server.down()


@pytest.fixture(autouse=True)
def subscriber_headers():
    payload = {'is_admin': False, 'is_staff': False, 'roles': ['subscriber']}
    token = jwt.encode(payload, settings.AUTH.SECRET_KEY, algorithm=settings.AUTH.ALGORITHM)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(autouse=True)
def not_subscriber_headers():
    payload = {'is_admin': False, 'is_staff': False, 'roles': ['guest']}
    token = jwt.encode(payload, settings.AUTH.SECRET_KEY, algorithm=settings.AUTH.ALGORITHM)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(autouse=True)
def invalid_headers():
    payload = {'is_admin': False, 'is_staff': False, 'roles': ['subscriber']}
    token = jwt.encode(payload, 'invalid_key', algorithm=settings.AUTH.ALGORITHM)
    return {'Authorization': f'Bearer {token}'}
