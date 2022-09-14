import pytest
from starlette import status

pytestmark = pytest.mark.asyncio

argvalues = [
    pytest.param(
        {'q': '*'}, status.HTTP_200_OK, 'search_film_select_all_query.json', id='ok_all_query'
    ),
    pytest.param(
        {'q': 'mark hamill'},
        status.HTTP_200_OK,
        'search_film_by_actor_query.json',
        id='ok_search_by_actor',
    ),
    pytest.param(
        {'q': 'some'}, status.HTTP_200_OK, 'search_film_some_query.json', id='ok_empty_query'
    ),
    pytest.param(
        {'q': '*', 'page': 10},
        status.HTTP_200_OK,
        'search_all_films_query_page_10.json',
        id='ok_query_page_10',
    ),
    pytest.param(
        {'q': 'some', 'limit': 33},
        status.HTTP_200_OK,
        'search_film_query_limit_33.json',
        id='ok_query_limit_33',
    ),
    pytest.param(
        {'q': 'star', 'page': 4, 'limit': 50},
        status.HTTP_200_OK,
        'search_film_query_page_4_and_limit_50.json',
        id='ok_query_page_4_and_limit_50',
    ),
    pytest.param(
        {'q': 'ffffooooo'},
        status.HTTP_404_NOT_FOUND,
        'not_found_response.json',
        id='not_found_by_query',
    ),
    pytest.param(
        {},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'requert_without_query.json',
        id='requert_without_query',
    ),
    pytest.param(
        {'q': 'some', 'limit': -10},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'negative_limit_response.json',
        id='invalid_query_limit_is_negative_number',
    ),
    pytest.param(
        {'q': 'some', 'page': -1},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'negative_page_response.json',
        id='invalid_query_page_is_negative_number',
    ),
    pytest.param(
        {'q': 'some', 'page': 'invalid_type'},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'invalid_page_type_data_response.json',
        id='invalid_query_page_type_error',
    ),
    pytest.param(
        {'q': 'some', 'limit': 'invalid_type'},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'invalid_limit_type_data_response.json',
        id='invalid_query_limit_type_error',
    ),
    pytest.param(
        {'q': 'some', 'limit': 'invalid type', 'page': 'invalid type'},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'invalid_both_page_and_limit_type_data.json',
        id='invalid_query_both_limit_and_page_type_error',
    ),
    pytest.param(
        {'limit': 'invalid type', 'page': 'invalid type'},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'invalid_page_and_limit_type_data_and_without_query.json',
        id='invalid_query_limit_and_page_type_and_without_query_error',
    ),
    pytest.param(
        {'q': 'some', 'limit': 100, 'page': 15},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'search_films_invalid_page_out_of_range.json',
        id='invalid_page_number_out_of_range',
    ),
]


@pytest.fixture(scope='function')
def expected_search_film_by_actor_not_subscriber(load_fixture):
    return load_fixture('search_film_by_actor_query_not_subscriber.json')


@pytest.mark.parametrize(
    'query_param, status_code, expected', argvalues, indirect=['expected']
)
async def test_search_film(
    es_load_films,
    clear_cache,
    make_get_request,
    v1_search_films_url,
    query_param,
    status_code,
    expected,
    subscriber_headers,
):
    response = await make_get_request(
        v1_search_films_url, params=query_param, headers=subscriber_headers
    )

    assert response.status == status_code
    assert len(response.body) == len(expected)

    if ('items', 'count') in response.body.keys():
        assert len(response.body['items']) == response.body['count']
        for idx, response_item in enumerate(response.body['items']):
            assert response_item == expected['items'][idx]
    else:
        assert response.body == expected


async def test_search_films_when_there_is_no_movies_index_in_es(
    clear_es_client_func,
    make_get_request,
    clear_cache,
    v1_search_films_url,
    expected_not_found,
    subscriber_headers,
):
    response = await make_get_request(
        v1_search_films_url, params={'q': 'some'}, headers=subscriber_headers
    )

    assert response.status == status.HTTP_404_NOT_FOUND
    assert len(response.body) == len(expected_not_found)
    assert response.body == expected_not_found


async def test_search_films_when_movies_index_in_es_is_empty(
    create_es_index_func,
    make_get_request,
    clear_cache,
    v1_search_films_url,
    expected_not_found,
    subscriber_headers,
):
    assert await create_es_index_func('movies') is True
    response = await make_get_request(
        v1_search_films_url, params={'q': 'some'}, headers=subscriber_headers
    )

    assert response.status == status.HTTP_404_NOT_FOUND
    assert len(response.body) == len(expected_not_found)
    assert response.body == expected_not_found


@pytest.mark.parametrize(
    'query_param, status_code, expected', argvalues[0:6], indirect=['expected']
)
async def test_search_films__cached_result(
    es_client_load,
    clear_cache,
    make_get_request,
    v1_search_films_url,
    expected,
    es_client,
    query_param,
    status_code,
    subscriber_headers,
):
    total, successes = await es_client_load(file='docs_for_es_movies.json', index='movies')
    assert total == successes

    await clear_cache.clear()

    test_call_count = 3  # Количество циклов "запрос get -> проверка response"
    counter = 0

    for _ in range(test_call_count):
        response = await make_get_request(
            v1_search_films_url, params=query_param, headers=subscriber_headers
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
            await es_client.indices.delete(index='movies')
            assert await es_client.indices.exists(index='movies') is False
