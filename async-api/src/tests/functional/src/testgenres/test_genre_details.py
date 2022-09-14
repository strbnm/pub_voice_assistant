from urllib.parse import urljoin

import pytest
from starlette import status

pytestmark = pytest.mark.asyncio


@pytest.fixture
def expected_detail_documentary(load_fixture):
    return load_fixture('genre_detail_documentary.json')


@pytest.fixture
def expected_detail_music(load_fixture):
    return load_fixture('genre_detail_music.json')


async def test_genre_detail_for_id_music_ok(
    es_load_genres,
    clear_cache,
    make_get_request,
    v1_genres_url,
    genre_id_music,
    expected_detail_music,
    subscriber_headers,
):
    genre_detail_url = urljoin(v1_genres_url, genre_id_music)
    response = await make_get_request(genre_detail_url, headers=subscriber_headers)

    assert response.status == status.HTTP_200_OK
    assert len(response.body) == len(expected_detail_music)
    assert response.body == expected_detail_music


async def test_genre_detail_for_id_documentary_ok(
    es_load_genres,
    clear_cache,
    make_get_request,
    v1_genres_url,
    genre_id_documentary,
    expected_detail_documentary,
    subscriber_headers,
):
    genre_detail_url = urljoin(v1_genres_url, genre_id_documentary)
    response = await make_get_request(genre_detail_url, headers=subscriber_headers)

    assert response.status == status.HTTP_200_OK
    assert len(response.body) == len(expected_detail_documentary)
    assert response.body == expected_detail_documentary


async def test_genre_detail_when_there_is_no_genres_index_in_es(
    clear_es_client_func,
    make_get_request,
    clear_cache,
    v1_genres_url,
    genre_id_music,
    expected_not_found,
    subscriber_headers,
):
    genre_detail_url = urljoin(v1_genres_url, genre_id_music)
    response = await make_get_request(genre_detail_url, headers=subscriber_headers)

    assert response.status == status.HTTP_404_NOT_FOUND
    assert len(response.body) == len(expected_not_found)
    assert response.body == expected_not_found


async def test_genre_detail_when_genres_index_in_es_is_empty(
    create_es_index_func,
    make_get_request,
    clear_cache,
    v1_genres_url,
    genre_id_music,
    expected_not_found,
    subscriber_headers,
):
    assert await create_es_index_func('genres') is True
    genre_detail_url = urljoin(v1_genres_url, genre_id_music)
    response = await make_get_request(genre_detail_url, headers=subscriber_headers)

    assert response.status == status.HTTP_404_NOT_FOUND
    assert len(response.body) == len(expected_not_found)
    assert response.body == expected_not_found


async def test_genre_detail__cached_result(
    es_client_load,
    clear_cache,
    make_get_request,
    v1_genres_url,
    genre_id_documentary,
    expected_detail_documentary,
    es_client,
    subscriber_headers,
):
    # создаем индекс 'genres' и загружаем в него данные
    total, successes = await es_client_load(file='docs_for_es_genres.json', index='genres')
    assert total == successes

    await clear_cache.clear()

    test_call_count = 3  # Количество циклов "запрос get -> проверка response"
    counter = 0
    genre_detail_url = urljoin(v1_genres_url, genre_id_documentary)

    for _ in range(test_call_count):
        response = await make_get_request(genre_detail_url, headers=subscriber_headers)
        assert response.status == status.HTTP_200_OK
        assert len(response.body) == len(expected_detail_documentary)
        assert response.body == expected_detail_documentary
        counter += 1
        if counter < 2:
            # после первого прогона удаляем индекс 'movies' в elasticsearch, чтобы убедиться, что дальнейшие запросы
            # используют кешированные данные и проверяем, что индекс не существует
            await es_client.indices.delete(index='genres')
            assert await es_client.indices.exists(index='genres') is False
