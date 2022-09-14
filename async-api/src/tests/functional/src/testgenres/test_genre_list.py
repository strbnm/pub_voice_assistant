import pytest
from starlette import status

pytestmark = pytest.mark.asyncio

argvalues = [
    pytest.param({}, status.HTTP_200_OK, 'genre_list_empty_query.json', id='ok_empty_query',),
    pytest.param(
        {'page': 3}, status.HTTP_200_OK, 'genre_list_query_page_3.json', id='ok_query_page_3',
    ),
    pytest.param(
        {'limit': 15},
        status.HTTP_200_OK,
        'genre_list_query_limit_15.json',
        id='ok_query_limit_15',
    ),
    pytest.param(
        {'page': 3, 'limit': 5},
        status.HTTP_200_OK,
        'genre_list_query_page_3_and_limit_5.json',
        id='ok_query_page_3_and_limit_5',
    ),
    pytest.param(
        {'limit': -1},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'negative_limit_response.json',
        id='invalid_query_limit_is_negative_number',
    ),
    pytest.param(
        {'page': -1},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'negative_page_response.json',
        id='invalid_query_page_is_negative_number',
    ),
    pytest.param(
        {'page': 'invalid_type'},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'invalid_page_type_data_response.json',
        id='invalid_query_page_type_error',
    ),
    pytest.param(
        {'limit': 'invalid_type'},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'invalid_limit_type_data_response.json',
        id='invalid_query_limit_type_error',
    ),
    pytest.param(
        {'limit': 'invalid type', 'page': 'invalid type'},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'invalid_both_page_and_limit_type_data.json',
        id='invalid_query_both_limit_and_page_type_error',
    ),
]


@pytest.fixture(scope='function')
def expected_cached_response(load_fixture):
    return load_fixture('genre_list_empty_query.json')


@pytest.fixture(scope='function')
def expected_default_page_and_limit(load_fixture):
    return load_fixture('genre_list_empty_query.json')


@pytest.mark.parametrize(
    'query_param, status_code, expected', argvalues, indirect=['expected']
)
async def test_film_list(
    es_load_genres,
    clear_cache,
    make_get_request,
    v1_genres_url,
    query_param,
    status_code,
    expected,
    subscriber_headers,
):
    response = await make_get_request(
        v1_genres_url, params=query_param, headers=subscriber_headers
    )

    assert response.status == status_code
    assert len(response.body) == len(expected)

    if ('items', 'count') in response.body.keys():
        assert len(response.body['items']) == response.body['count']
        for idx, response_item in enumerate(response.body['items']):
            assert response_item == expected['items'][idx]
    else:
        assert response.body == expected


async def test_genre_list_use_default_page_and_limit_ok(
    es_load_genres,
    make_get_request,
    clear_cache,
    v1_genres_url,
    expected_default_page_and_limit,
    default_page,
    default_page_limit,
    subscriber_headers,
):
    response = await make_get_request(v1_genres_url, headers=subscriber_headers)

    assert response.status == status.HTTP_200_OK
    assert len(response.body) == len(expected_default_page_and_limit)
    assert response.body == expected_default_page_and_limit
    assert response.body['page'] == default_page
    assert response.body['count'] == default_page_limit
    assert len(response.body['items']) == default_page_limit


async def test_film_list_when_there_is_no_genres_index_in_es(
    clear_es_client_func,
    make_get_request,
    clear_cache,
    v1_genres_url,
    expected_not_found,
    subscriber_headers,
):
    response = await make_get_request(v1_genres_url, params={}, headers=subscriber_headers)

    assert response.status == status.HTTP_404_NOT_FOUND
    assert len(response.body) == len(expected_not_found)
    assert response.body == expected_not_found


async def test_genre_list_when_genres_index_in_es_is_empty(
    create_es_index_func,
    make_get_request,
    clear_cache,
    v1_genres_url,
    expected_not_found,
    subscriber_headers,
):
    assert await create_es_index_func('genres') is True
    response = await make_get_request(v1_genres_url, params={}, headers=subscriber_headers)

    assert response.status == status.HTTP_404_NOT_FOUND
    assert len(response.body) == len(expected_not_found)
    assert response.body == expected_not_found


# прогоняем тесты на части заданных в argvalues параметрических кейсах, возвращающих статус 200
@pytest.mark.parametrize(
    'query_param, status_code, expected', argvalues[0:3], indirect=['expected']
)
async def test_genre_list__cached_result(
    es_client_load,
    clear_cache,
    make_get_request,
    v1_genres_url,
    expected,
    es_client,
    query_param,
    status_code,
    subscriber_headers,
):
    # создаем индекс 'genres' и загружаем в него данные
    total, successes = await es_client_load(file='docs_for_es_genres.json', index='genres')
    assert total == successes

    await clear_cache.clear()

    test_call_count = 3  # Количество циклов "запрос get -> проверка response"
    counter = 0

    for _ in range(test_call_count):
        response = await make_get_request(
            v1_genres_url, params=query_param, headers=subscriber_headers
        )
        assert response.status == status_code
        assert len(response.body) == len(expected)
        assert len(response.body['items']) == response.body['count']
        for idx, response_item in enumerate(response.body['items']):
            assert response_item == expected['items'][idx]
        counter += 1
        if counter < 2:
            # после первого прогона удаляем индекс 'movies' в elasticsearch, чтобы убедиться, что дальнейшие запросы
            # используют кешированные данные и проверяем, что индекс не существует
            await es_client.indices.delete(index='genres')
            assert await es_client.indices.exists(index='genres') is False
