import http
from http import HTTPStatus
from unittest.mock import ANY

import pytest
from functional.src.api.v1.admin.conftest import create_user

from tests.functional.src.api.v1.admin.common_functions import get_response


@pytest.fixture
def temp_user(app, temp_user_username, temp_user_password, temp_user_email, guest_role):
    return create_user(
        app, temp_user_username, temp_user_password, temp_user_email, guest_role
    )


@pytest.fixture
def expected_base_roles_list():
    expected = {
        'count': 3,
        'total_pages': 1,
        'prev': None,
        'next': None,
        'results': [
            {
                'id': ANY,
                'name': 'guest',
                'description': 'Пользователь онлайн-кинотеатра с базовыми разрешениями.',
            },
            {
                'id': ANY,
                'name': 'staff',
                'description': 'Сотрудник кинотеатра, имеющий доступ к службе администрирования.',
            },
            {
                'id': ANY,
                'name': 'superuser',
                'description': 'Пользователь с правами администратора (есть все разрешения без их явного назначения).',
            },
        ],
    }
    return expected


@pytest.fixture
def expected_superuser_roles_list():
    expected = {
        'count': 1,
        'total_pages': 1,
        'prev': None,
        'next': None,
        'results': [
            [
                {
                    'id': ANY,
                    'name': 'superuser',
                    'description': 'Пользователь с правами администратора (есть все разрешения без их явного назначения).',
                }
            ]
        ],
    }
    return expected


@pytest.fixture
def expected_quest_roles_list():
    expected = {
        'count': 1,
        'total_pages': 1,
        'prev': None,
        'next': None,
        'results': [
            [
                {
                    'id': ANY,
                    'name': 'guest',
                    'description': 'Пользователь онлайн-кинотеатра с базовыми разрешениями.',
                }
            ]
        ],
    }
    return expected


@pytest.fixture
def expected_staff_roles_list():
    expected = {
        'count': 1,
        'total_pages': 1,
        'prev': None,
        'next': None,
        'results': [
            [
                {
                    'id': ANY,
                    'name': 'staff',
                    'description': 'Сотрудник кинотеатра, имеющий доступ к службе администрирования.',
                }
            ]
        ],
    }
    return expected


def test_get_roles(
    client,
    clear_db,
    temp_superuser_auth_access_header,
    temp_staff_user_auth_access_header,
    expected_base_roles_list,
):
    url = '/api/v1/roles/'
    for header in (temp_superuser_auth_access_header, temp_staff_user_auth_access_header):
        response = get_response(
            client.get, headers=header, url=url, query_param={'page': 1, 'per_page': 5}
        )

        assert response.status_code == http.HTTPStatus.OK
        assert response.json == expected_base_roles_list


def test_get_roles_of_user_ok(
    client,
    clear_db,
    temp_superuser_auth_access_header,
    temp_user,
    temp_staff_user,
    temp_superuser,
    expected_quest_roles_list,
    expected_staff_roles_list,
    expected_superuser_roles_list,
):
    url_list = [
        f'/api/v1/users/{temp_user.id}/roles',
        f'/api/v1/users/{temp_staff_user.id}/roles',
        f'/api/v1/users/{temp_superuser.id}/roles',
    ]
    expected_list = [
        expected_quest_roles_list,
        expected_staff_roles_list,
        expected_superuser_roles_list,
    ]
    for url, expected_role in zip(url_list, expected_list):
        response = get_response(
            client.get,
            headers=temp_superuser_auth_access_header,
            url=url,
            query_param={'page': 1, 'per_page': 5},
        )
        # assert response.status_code == http.HTTPStatus.OK
        assert response.json == expected_role


def test_bad_authorizations_get_roles(
    client, app, clear_db, temp_user_auth_access_header,
):
    url = '/api/v1/roles/'
    response = get_response(client.get, headers=temp_user_auth_access_header, url=url)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_bad_authorizations_get_roles_of_users(
    client, app, clear_db, temp_user_auth_access_header, temp_superuser
):
    url = f'/api/v1/users/{temp_superuser.id}/roles'
    response = get_response(client.get, headers=temp_user_auth_access_header, url=url)
    assert response.status_code == HTTPStatus.FORBIDDEN
