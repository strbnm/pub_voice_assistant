from http import HTTPStatus

from tests.functional.src.api.v1.admin.common_functions import get_response


def test_delete_role(client, app, clear_db, temp_superuser_auth_access_header, guest_role):
    role = {'name': 'testing', 'description': 'testing'}
    new_role = get_response(
        client.post, temp_superuser_auth_access_header, '/api/v1/roles/', body_params=role
    ).json
    url = f'/api/v1/roles/{new_role["id"]}'
    response = get_response(client.delete, temp_superuser_auth_access_header, url)
    assert response.status_code == HTTPStatus.NO_CONTENT
    response = get_response(client.delete, temp_superuser_auth_access_header, url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    url = f'/api/v1/roles/{guest_role.id}'
    response = get_response(client.delete, temp_superuser_auth_access_header, url)
    assert response.status_code == HTTPStatus.CONFLICT


def test_bad_authorizations_delete_role(
    client, app, clear_db, temp_user_auth_access_header, temp_staff_user_auth_access_header
):
    url = '/api/v1/roles/'
    for header in (temp_user_auth_access_header, temp_staff_user_auth_access_header):
        response = get_response(client.post, headers=header, url=url)
        assert response.status_code == HTTPStatus.FORBIDDEN
