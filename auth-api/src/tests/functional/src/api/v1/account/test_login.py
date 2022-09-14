import http

import pytest

from app.models.roles import ProtectedRoleEnum
from app.models.user import User
from tests.functional.utils import decode_jwt

argvalues = [
    pytest.param(
        {'password': '#Test1234#'},
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_login.json',
        id='missing_required_login',
    ),
    pytest.param(
        {},
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_password_and_login.json',
        id='missing_required_both_password_and_login.json',
    ),
    pytest.param(
        {'login': 'test@example.com'},
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_password.json',
        id='missing_required_password',
    ),
    pytest.param(
        {'login': 'not_exist_user@example.com', 'password': '#Test1234#'},
        http.HTTPStatus.UNAUTHORIZED,
        'expected_error_unauthorized.json',
        id='user_does_not_exist',
    ),
    pytest.param(
        {'login': 'test@example.com', 'password': '#Wrong_password1#'},
        http.HTTPStatus.UNAUTHORIZED,
        'expected_error_unauthorized.json',
        id='user_with_wrong_password',
    ),
]


def test_login_ok(client, clear_db, email, account_temp_user, password):
    response = client.post(path='/api/v1/login', data={'login': email, 'password': password})
    assert response.status_code == http.HTTPStatus.OK
    result = response.json
    assert 'access_token' in result
    access_token = decode_jwt(result['access_token'])
    assert access_token.type == 'access'
    assert access_token.sub == str(account_temp_user.id)
    assert ProtectedRoleEnum.guest.value in access_token.roles
    assert 'refresh_token' in result
    refresh_token = decode_jwt(result['refresh_token'])
    assert refresh_token.type == 'refresh'
    assert refresh_token.sub == str(account_temp_user.id)


def test_login_user_with_valid_access_token_ok(
    client, clear_db, account_temp_user, valid_jwt_pair, app, email
):
    response = client.post(
        path='/api/v1/login', headers={'Authorization': f'Bearer {valid_jwt_pair[0]}'}
    )
    assert response.status_code == http.HTTPStatus.OK
    current_user_id = decode_jwt(valid_jwt_pair[0]).sub
    with app.app_context():
        user = User.query.filter_by(id=current_user_id).one_or_none()
        assert response.json == f'Пользователь {email} уже аутентифицирован'
        assert user.email == email


def test_login_user_with_invalid_access_token_ok(
    client, clear_db, account_temp_user, invalid_jwt_pair, load_fixture
):
    response = client.post(
        path='/api/v1/login', headers={'Authorization': f'Bearer {invalid_jwt_pair[0]}'}
    )
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED
    assert response.json == load_fixture('expected_error_unauthorized_by_token.json')


@pytest.mark.parametrize('body_param, status_code, expected', argvalues, indirect=['expected'])
def test_login_with_bad_request_param(
    client, clear_db, account_temp_user, body_param, status_code, expected
):
    response = client.post(path='/api/v1/login', data=body_param)
    assert response.status_code == status_code
    assert response.json == expected
