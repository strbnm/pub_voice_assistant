import pytest
from starlette import status

pytestmark = pytest.mark.asyncio


@pytest.fixture
def expected_detail(load_fixture):
    return load_fixture('film_detail.json')


async def test_film_detail(
    es_load_films,
    clear_cache,
    make_get_request,
    v1_film_detail_url,
    expected_detail,
    subscriber_headers,
):
    response = await make_get_request(v1_film_detail_url, headers=subscriber_headers)

    assert response.status == status.HTTP_200_OK
    assert len(response.body) == len(expected_detail)
    assert response.body == expected_detail


async def test_film_detail_with_not_subscriber__unauthorized(
    es_load_films,
    clear_cache,
    make_get_request,
    v1_film_detail_url,
    expected_detail,
    not_subscriber_headers,
):
    response = await make_get_request(v1_film_detail_url, headers=not_subscriber_headers)

    assert response.status == status.HTTP_403_FORBIDDEN


async def test_film_detail_with_invalid_token__unauthorized(
    es_load_films,
    clear_cache,
    make_get_request,
    v1_film_detail_url,
    expected_detail,
    invalid_headers,
):
    response = await make_get_request(v1_film_detail_url, headers=invalid_headers)

    assert response.status == status.HTTP_403_FORBIDDEN


async def test_film_detail_when_there_is_no_movies_index_in_es(
    clear_es_client_func,
    make_get_request,
    clear_cache,
    v1_film_detail_url,
    expected_not_found,
    subscriber_headers,
):
    response = await make_get_request(v1_film_detail_url, headers=subscriber_headers)
    assert response.status == status.HTTP_404_NOT_FOUND
    assert len(response.body) == len(expected_not_found)
    assert response.body == expected_not_found


async def test_film_detail_when_movies_index_in_es_is_empty(
    create_es_index_func,
    make_get_request,
    clear_cache,
    v1_film_detail_url,
    expected_not_found,
    subscriber_headers,
):
    assert await create_es_index_func('movies') is True
    response = await make_get_request(v1_film_detail_url, headers=subscriber_headers)

    assert response.status == status.HTTP_404_NOT_FOUND
    assert len(response.body) == len(expected_not_found)
    assert response.body == expected_not_found


async def test_film_detail__cached_result(
    es_client_load,
    clear_cache,
    make_get_request,
    v1_film_detail_url,
    expected_detail,
    es_client,
    subscriber_headers,
):
    # создаем индекс 'movies' и загружаем в него данные
    total, successes = await es_client_load(file='docs_for_es_movies.json', index='movies')
    assert total == successes

    await clear_cache.clear()

    test_call_count = 3  # Количество циклов "запрос get -> проверка response"
    counter = 0

    for _ in range(test_call_count):
        response = await make_get_request(v1_film_detail_url, headers=subscriber_headers)
        assert response.status == status.HTTP_200_OK
        assert len(response.body) == len(expected_detail)
        assert response.body == expected_detail
        counter += 1
        if counter < 2:
            # после первого прогона удаляем индекс 'movies' в elasticsearch, чтобы убедиться, что дальнейшие запросы
            # используют кешированные данные и проверяем, что индекс не существует
            await es_client.indices.delete(index='movies')
            assert await es_client.indices.exists(index='movies') is False
