import pytest


@pytest.fixture
def v1_genres_url():
    return '/api/v1/genre/'


@pytest.fixture
def genre_id_music():
    return '56b541ab-4d66-4021-8708-397762bff2d4'


@pytest.fixture
def genre_id_documentary():
    return '6d141ad2-d407-4252-bda4-95590aaf062a'


@pytest.fixture(scope='module')
async def es_load_genres(es_client_load):
    total, successes = await es_client_load(file='docs_for_es_genres.json', index='genres')
    assert total == successes
