from urllib.parse import urljoin

import pytest


@pytest.fixture
def v1_films_url():
    return '/api/v1/film/'


@pytest.fixture
def v1_search_films_url():
    return 'api/v1/film/search'


@pytest.fixture
def v1_search_films_by_person_url():
    return '/api/v1/person/{person_id}/film'


@pytest.fixture
def person_id():
    return '26e83050-29ef-4163-a99d-b546cac208f8'  # Person: Mark Hamill


@pytest.fixture
def film_id():
    return '0312ed51-8833-413f-bff5-0e139c11264a'  # Filmwork: Star Wars: Episode V - The Empire Strikes Back


@pytest.fixture
async def v1_film_detail_url(v1_films_url, film_id):
    return urljoin(v1_films_url, film_id)


@pytest.fixture(scope='module')
async def es_load_films(es_client_load):
    total, successes = await es_client_load(file='docs_for_es_movies.json', index='movies')
    assert total == successes
