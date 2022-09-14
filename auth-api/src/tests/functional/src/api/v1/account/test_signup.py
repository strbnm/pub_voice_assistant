import http

import pytest
from functional.utils import UserSignupResponseModel

from app.models.user import User

argvalues = [
    pytest.param(
        {},
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_all_param.json',
        id='missing_all_required_param',
    ),
    pytest.param(
        {
            'email': 'test_signup@example.com',
            'password': '#Testsignup1#',
            'first_name': 'John',
            'last_name': 'Smith',
        },
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_username.json',
        id='missing_required_username',
    ),
    pytest.param(
        {
            'username': 'test_signup',
            'password': '#Testsignup1#',
            'first_name': 'John',
            'last_name': 'Smith',
        },
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_email.json',
        id='missing_required_email',
    ),
    pytest.param(
        {
            'username': 'test_signup',
            'email': 'test_signup@example.com',
            'first_name': 'John',
            'last_name': 'Smith',
        },
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_password.json',
        id='missing_required_password',
    ),
    pytest.param(
        {'username': 'test_signup', 'first_name': 'John', 'last_name': 'Smith'},
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_both_email_and_password.json',
        id='missing_required_both_email_and_password',
    ),
    pytest.param(
        {'password': '#Testsignup1#', 'first_name': 'John', 'last_name': 'Smith'},
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_both_email_and_username.json',
        id='missing_required_both_email_and_username',
    ),
    pytest.param(
        {'email': 'test_signup@example.com', 'first_name': 'John', 'last_name': 'Smith'},
        http.HTTPStatus.BAD_REQUEST,
        'expected_error_missing_both_username_and_password.json',
        id='missing_required_both_username_and_password',
    ),
]


@pytest.fixture
def temp_user_signup():
    return {
        'username': 'test_signup',
        'email': 'test_signup@example.com',
        'password': '#Testsignup1#',
        'first_name': 'John',
        'last_name': 'Smith',
    }


@pytest.fixture
def temp_user_signup_only_required_param():
    return {
        'username': 'test_signup',
        'email': 'test_signup@example.com',
        'password': '#Testsignup1#',
    }


def test_signup_ok(client, clear_db, temp_user_signup, app):
    response = client.post(path='/api/v1/signup', data=temp_user_signup)
    assert response.status_code == http.HTTPStatus.CREATED
    new_user = UserSignupResponseModel(**response.json)
    with app.app_context():
        user_in_database = User.query.filter_by(email=temp_user_signup['email']).one_or_none()
        assert user_in_database
        assert new_user.id == user_in_database.id
        assert new_user.username == user_in_database.username == temp_user_signup['username']
        assert new_user.email == user_in_database.email == temp_user_signup['email']
        assert (
            new_user.first_name == user_in_database.first_name == temp_user_signup['first_name']
        )
        assert (
            new_user.last_name == user_in_database.last_name == temp_user_signup['last_name']
        )
        assert new_user.is_active == user_in_database.active
        assert new_user.created_at == user_in_database.created_at


def test_signup_only_required_param_ok(
    client, clear_db, temp_user_signup_only_required_param, app
):
    response = client.post(path='/api/v1/signup', data=temp_user_signup_only_required_param)
    assert response.status_code == http.HTTPStatus.CREATED
    new_user = UserSignupResponseModel(**response.json)
    with app.app_context():
        user_in_database = User.query.filter_by(
            email=temp_user_signup_only_required_param['email']
        ).one_or_none()
        assert user_in_database
        assert new_user.id == user_in_database.id
        assert (
            new_user.username == user_in_database.username == temp_user_signup_only_required_param['username']
        )
        assert (
            new_user.email == user_in_database.email == temp_user_signup_only_required_param['email']
        )
        assert new_user.first_name is None
        assert new_user.last_name is None
        assert new_user.is_active == user_in_database.active
        assert new_user.created_at == user_in_database.created_at


@pytest.mark.parametrize('body_param, status_code, expected', argvalues, indirect=['expected'])
def test_signup_with_bad_request_param(
    client, clear_db, temp_user_signup, app, body_param, status_code, expected
):
    response = client.post(path='/api/v1/signup', data=body_param)
    assert response.status_code == status_code
    assert response.json == expected
    with app.app_context():
        user_in_database = User.query.filter_by(email=temp_user_signup['email']).one_or_none()
        assert not user_in_database


def test_signup_same_user(client, clear_db, temp_user_signup, app, load_fixture):
    response = client.post(path='/api/v1/signup', data=temp_user_signup)
    assert response.status_code == http.HTTPStatus.CREATED
    response = client.post(path='/api/v1/signup', data=temp_user_signup)
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json == load_fixture('expected_exist_user.json')
