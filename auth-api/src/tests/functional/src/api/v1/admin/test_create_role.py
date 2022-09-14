from http import HTTPStatus

import pytest

from tests.functional.src.api.v1.admin.common_functions import get_response

argvalues = [
    pytest.param(
        {'name': 'test_role', 'description': 'test'}, HTTPStatus.CREATED, id='ok_query',
    ),
    pytest.param(
        {'name': 'superuser', 'description': 'duplicate'},
        HTTPStatus.CONFLICT,
        id='conflict_duplicate',
    ),
    pytest.param(
        {'name': 'without description'}, HTTPStatus.BAD_REQUEST, id='without_description',
    ),
    pytest.param({}, HTTPStatus.BAD_REQUEST, id='empty_body',),
]


@pytest.mark.parametrize('body_params, status_code', argvalues)
def test_create_role(
    client, app, clear_db, temp_superuser_auth_access_header, body_params, status_code
):
    url = '/api/v1/roles/'
    response = get_response(
        client.post, temp_superuser_auth_access_header, url, body_params=body_params
    )

    assert response.status_code == status_code


def test_bad_authorizations_create_role(
    client, app, clear_db, temp_user_auth_access_header, temp_staff_user_auth_access_header
):
    url = '/api/v1/roles/'
    for header in (temp_user_auth_access_header, temp_staff_user_auth_access_header):
        response = get_response(client.post, header, url)
        assert response.status_code == HTTPStatus.FORBIDDEN
