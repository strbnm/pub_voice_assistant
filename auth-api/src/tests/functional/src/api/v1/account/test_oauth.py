import http
import uuid

import pytest

from app.oauth import compliance_fix


@pytest.fixture
def unknown_social_name() -> str:
    unknown_social_name = 'any_social_name'
    return unknown_social_name


def test_login_unknown_social_name(client, unknown_social_name):
    response = client.get(path=f'/api/v1/login/{unknown_social_name}')
    assert response.status_code == http.HTTPStatus.NOT_FOUND


def test_auth_unknown_social_name(client, unknown_social_name):
    response = client.get(path=f'/api/v1/auth/{unknown_social_name}')
    assert response.status_code == http.HTTPStatus.NOT_FOUND


def test_compliance_fix():
    test_uuid = uuid.uuid4().__str__()
    input_user_data = {
        'id': test_uuid,
        'login': 'test',
        'client_id': uuid.uuid4().__str__(),
        'display_name': 'display name',
        'real_name': 'real name',
        'first_name': 'first',
        'last_name': 'last',
        'sex': 'female',
        'default_email': 'test@test.ru',
        'emails': ['test@test.ru'],
        'psuid': 'x.xxx.xxx.xxx',
    }

    expected = {
        'sub': test_uuid,
        'name': 'display name',
        'email': 'test@test.ru',
    }

    result = compliance_fix(None, input_user_data)
    assert result == expected
