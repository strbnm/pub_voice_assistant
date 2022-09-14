from http import HTTPStatus
from uuid import uuid4

import pytest
from functional.src.api.v1.admin.common_functions import get_response

argvalues = [
    pytest.param({'name': 'foo', 'description': 'bar'}, HTTPStatus.CREATED, id='CREATED',),
    pytest.param({'name': 'foo'}, HTTPStatus.CREATED, id='without_description',),
    pytest.param({'description': 'bar'}, HTTPStatus.CREATED, id='without_name',),
    pytest.param({}, HTTPStatus.BAD_REQUEST, id='empty',),
]


@pytest.mark.parametrize('body_params, status_code', argvalues)
def test_change_role(
    client,
    app,
    clear_db,
    temp_superuser_auth_access_header,
    temp_user,
    body_params,
    status_code,
):
    role = {'name': 'testing', 'description': 'testing'}
    role = get_response(
        client.post, temp_superuser_auth_access_header, '/api/v1/roles/', body_params=role
    ).json['id']

    url = f'/api/v1/roles/{role}'
    response = get_response(
        client.put, temp_superuser_auth_access_header, url, body_params=body_params
    )
    assert response.status_code == HTTPStatus.CREATED
    if status_code == HTTPStatus.CREATED:
        result = response.json
        assert result['name'] == body_params.get('name', result['name'])
        assert result['description'] == body_params.get('description', result['description'])
        assert result['id'] == role


def test_change_role_with_wrong_items(
    client, app, clear_db, temp_superuser_auth_access_header
):
    url = f'/api/v1/roles/{uuid4()}'
    response = get_response(client.put, temp_superuser_auth_access_header, url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_bad_authorizations_change_role(
    client,
    app,
    clear_db,
    temp_user_auth_access_header,
    temp_staff_user_auth_access_header,
    temp_superuser_auth_access_header,
):
    role = {'name': 'testing', 'description': 'testing'}
    role = get_response(
        client.post, temp_superuser_auth_access_header, '/api/v1/roles/', body_params=role
    ).json['id']

    url = f'/api/v1/users/{uuid4()}/roles/{uuid4()}'
    for header in (temp_user_auth_access_header, temp_staff_user_auth_access_header):
        response = get_response(client.put, header, url)
        assert response.status_code == HTTPStatus.FORBIDDEN
