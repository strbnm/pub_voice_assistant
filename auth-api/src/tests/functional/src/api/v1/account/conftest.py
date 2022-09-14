import http

import pytest

from app.database import session_scope
from app.datastore import user_datastore
from app.models.roles import ProtectedRoleEnum
from tests.functional.utils import UserTestModel


@pytest.fixture(name='username')
def temp_user_username():
    return 'test'


@pytest.fixture(name='email')
def temp_user_email():
    return 'test@example.com'


@pytest.fixture(name='password')
def temp_user_password():
    return '#Test1234#'


@pytest.fixture
def account_temp_user(app, username, password, email):
    with app.app_context():
        with session_scope():
            user = user_datastore.create_user(
                username=username, password=password, email=email,
            )
            user_datastore.add_role_to_user(user, ProtectedRoleEnum.guest.value)
            return UserTestModel(**user.__dict__)


@pytest.fixture(name='valid_jwt_pair')
def user_valid_jwt_pair_after_login(client, clear_db, email, password, account_temp_user):
    response = client.post(path='/api/v1/login', data={'login': email, 'password': password},)
    assert response.status_code == http.HTTPStatus.OK
    result = response.json
    assert 'access_token' in result
    assert 'refresh_token' in result
    return result['access_token'], result['refresh_token']


@pytest.fixture(name='invalid_jwt_pair')
def user_invalid_jwt_pair_after_login(client, clear_db, account_temp_user, valid_jwt_pair):
    access_token, refresh_token = valid_jwt_pair
    response = client.post(
        path='/api/v1/logout', headers={'Authorization': f'Bearer {access_token}'}
    )
    assert response.status_code == http.HTTPStatus.OK
    result = response.json
    assert 'message' in result
    assert result['message'] == 'Вы вышли из аккаунта'
    return access_token, refresh_token


@pytest.fixture(name='access_header')
def temp_user_auth_access_header(valid_jwt_pair) -> dict[str, str]:
    access_token, _ = valid_jwt_pair
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture(name='refresh_header')
def temp_user_auth_refresh_header(valid_jwt_pair) -> dict[str, str]:
    _, refresh_token = valid_jwt_pair
    return {'Authorization': f'Bearer {refresh_token}'}
