import http

import pytest

from app.datastore import user_datastore

argvalues = [
    pytest.param(
        {},
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_all_passwords.json',
        id='missing_required_both_passwords',
    ),
    pytest.param(
        {'old_password': '#Test1234#'},
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_new_password.json',
        id='missing_required_new_password',
    ),
    pytest.param(
        {'new_password': '!Test1234!'},
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_old_password.json',
        id='missing_required_old_password',
    ),
]


@pytest.fixture
def new_password():
    return '!Test1234!'


@pytest.fixture
def wrong_password():
    return '!Wrong_password1234!'


def test_change_password_ok(
    client, clear_db, app, account_temp_user, access_header, password, new_password
):
    response = client.patch(
        path='/api/v1/user/password',
        headers=access_header,
        data={'old_password': password, 'new_password': new_password},
    )
    assert response.status_code == http.HTTPStatus.OK
    with app.app_context():
        user = user_datastore.find_user(id=account_temp_user.id)
        assert user.check_password(new_password)
    response = client.patch(
        path='/api/v1/user/password',
        headers=access_header,
        data={'old_password': password, 'new_password': new_password},
    )
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_change_password_with_wrong_password(
    client, clear_db, account_temp_user, access_header, wrong_password, new_password
):
    response = client.patch(
        path='/api/v1/user/password',
        headers=access_header,
        data={'old_password': wrong_password, 'new_password': new_password},
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_change_password_with_invalid_token(
    client, clear_db, account_temp_user, invalid_jwt_pair, password, new_password
):
    response = client.patch(
        path='/api/v1/user/password',
        headers={'Authorization': f'Bearer {invalid_jwt_pair[0]}'},
        data={'old_password': password, 'new_password': new_password},
    )
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize('body_param, status_code, expected', argvalues, indirect=['expected'])
def test_change_password_with_bad_request_param(
    client, clear_db, account_temp_user, access_header, body_param, status_code, expected
):
    response = client.patch('/api/v1/user/password', headers=access_header, data=body_param)
    assert response.status_code == status_code
    assert response.json == expected
