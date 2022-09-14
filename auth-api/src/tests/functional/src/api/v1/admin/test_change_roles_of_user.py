from http import HTTPStatus
from uuid import uuid4

from functional.src.api.v1.admin.common_functions import get_response


def test_change_role_of_user(
    client, app, clear_db, temp_superuser_auth_access_header, temp_user
):
    role = {'name': 'testing', 'description': 'testing'}
    role = get_response(
        client.post, temp_superuser_auth_access_header, '/api/v1/roles/', body_params=role
    ).json['id']

    url = f'/api/v1/users/{temp_user.id}/roles/{role}'
    response = get_response(client.put, temp_superuser_auth_access_header, url)
    assert response.status_code == HTTPStatus.CREATED

    response = get_response(client.put, temp_superuser_auth_access_header, url)
    assert response.status_code == HTTPStatus.CONFLICT

    response = get_response(client.delete, temp_superuser_auth_access_header, url)
    assert response.status_code == HTTPStatus.NO_CONTENT

    url = f'/api/v1/users/{temp_user.id}/roles/{uuid4()}'
    response = get_response(client.put, temp_superuser_auth_access_header, url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = get_response(client.delete, temp_superuser_auth_access_header, url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    url = f'/api/v1/users/{uuid4()}/roles/{role}'
    response = get_response(client.put, temp_superuser_auth_access_header, url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = get_response(client.delete, temp_superuser_auth_access_header, url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_bad_authorizations_change_role_of_user(
    client, app, clear_db, temp_user_auth_access_header, temp_staff_user_auth_access_header
):
    url = f'/api/v1/users/{uuid4()}/roles/{uuid4()}'
    for header in (temp_user_auth_access_header, temp_staff_user_auth_access_header):
        response = get_response(client.put, header, url)
        assert response.status_code == HTTPStatus.FORBIDDEN
