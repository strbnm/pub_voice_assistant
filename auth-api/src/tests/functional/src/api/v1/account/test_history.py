import http
from time import sleep

import pytest


@pytest.fixture
def fake_user_agent():
    return {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
    }


def test_user_history_ok(
    client, clear_db, account_temp_user, fake_user_agent, access_header, email, password
):
    n = 3
    page = 1
    per_page = 7
    for _ in range(n):
        response = client.post(
            path='/api/v1/login',
            headers=fake_user_agent,
            data={'login': email, 'password': password},
        )
        assert response.status_code == http.HTTPStatus.OK
        sleep(0.5)
    for _ in range(n):
        response = client.post(
            path='/api/v1/login', data={'login': email, 'password': password},
        )
        assert response.status_code == http.HTTPStatus.OK
        sleep(0.5)
    response = client.get(
        path='/api/v1/user/history',
        headers=access_header,
        query_string={'page': page, 'per_page': per_page},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json['count'] == n * 2 + 1  # один вход при генерации фикстуры access_token
    assert response.json['total_pages'] == 1
    count_fake_user_agent = 0
    for item in response.json['results']:
        assert item['user_id'] == str(account_temp_user.id)
        if item['user_agent'] == fake_user_agent['User-Agent']:
            count_fake_user_agent += 1
    assert count_fake_user_agent == n


def test_user_history_with_invalid_access_token(
    client, clear_db, invalid_jwt_pair, account_temp_user
):
    response = client.get(
        path='/api/v1/user/history',
        headers={'Authorization': f'Bearer {invalid_jwt_pair[0]}'},
        query_string={'page': 1, 'per_page': 5},
    )
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED
