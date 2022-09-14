from urllib.parse import urljoin

import pytest
from starlette import status

pytestmark = pytest.mark.asyncio


@pytest.fixture
def expected_detail(load_fixture):
    return load_fixture('person_detail.json')


async def test_person_detail_ok(
    es_load_persons,
    clear_cache,
    make_get_request,
    v1_persons_url,
    person_id,
    expected_detail,
    subscriber_headers,
):
    person_detail_url = urljoin(v1_persons_url, person_id)
    response = await make_get_request(person_detail_url, headers=subscriber_headers)

    assert response.status == status.HTTP_200_OK
    assert len(response.body) == len(expected_detail)
    assert response.body == expected_detail
    assert response.body['full_name'] == expected_detail['full_name']


async def test_person_detail_when_there_is_no_persons_index_in_es(
    clear_es_client_func,
    make_get_request,
    clear_cache,
    v1_persons_url,
    person_id,
    expected_not_found,
    subscriber_headers,
):
    person_detail_url = urljoin(v1_persons_url, person_id)
    response = await make_get_request(person_detail_url, headers=subscriber_headers)

    assert response.status == status.HTTP_404_NOT_FOUND
    assert len(response.body) == len(expected_not_found)
    assert response.body == expected_not_found


async def test_person_detail_when_persons_index_in_es_is_empty(
    create_es_index_func,
    make_get_request,
    clear_cache,
    v1_persons_url,
    person_id,
    expected_not_found,
    subscriber_headers,
):
    assert await create_es_index_func('persons') is True
    person_detail_url = urljoin(v1_persons_url, person_id)
    response = await make_get_request(person_detail_url, headers=subscriber_headers)

    assert response.status == status.HTTP_404_NOT_FOUND
    assert len(response.body) == len(expected_not_found)
    assert response.body == expected_not_found


async def test_person_detail__cached_result(
    es_client_load,
    clear_cache,
    make_get_request,
    v1_persons_url,
    person_id,
    expected_detail,
    es_client,
    subscriber_headers,
):
    # создаем индекс 'persons' и загружаем в него данные
    total, successes = await es_client_load(file='docs_for_es_persons.json', index='persons')
    assert total == successes

    await clear_cache.clear()

    test_call_count = 3  # Количество циклов "запрос get -> проверка response"
    counter = 0
    person_detail_url = urljoin(v1_persons_url, person_id)

    for _ in range(test_call_count):
        response = await make_get_request(person_detail_url, headers=subscriber_headers)
        assert response.status == status.HTTP_200_OK
        assert len(response.body) == len(expected_detail)
        assert response.body == expected_detail
        counter += 1
        if counter < 2:
            # после первого прогона удаляем индекс 'movies' в elasticsearch, чтобы убедиться, что дальнейшие запросы
            # используют кешированные данные и проверяем, что индекс не существует
            await es_client.indices.delete(index='persons')
            assert await es_client.indices.exists(index='persons') is False
