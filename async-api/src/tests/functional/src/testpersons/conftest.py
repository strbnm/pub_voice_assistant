from urllib.parse import urljoin

import pytest


@pytest.fixture
def v1_persons_url():
    return '/api/v1/person/'


@pytest.fixture
def v1_search_persons_url():
    return '/api/v1/person/search'


@pytest.fixture
def person_id():
    return '26e83050-29ef-4163-a99d-b546cac208f8'  # Person: Mark Hamill


@pytest.fixture
async def v1_person_detail_url(v1_persons_url, person_id):
    return urljoin(v1_persons_url, person_id)


@pytest.fixture(scope='module')
async def es_load_persons(es_client_load):
    total, successes = await es_client_load(file='docs_for_es_persons.json', index='persons')
    assert total == successes
