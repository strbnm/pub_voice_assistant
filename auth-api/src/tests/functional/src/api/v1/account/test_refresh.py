import http


def test_refresh_ok(client, clear_db, account_temp_user, refresh_header):
    response = client.post(path='/api/v1/refresh', headers=refresh_header)
    assert response.status_code == http.HTTPStatus.OK
    result = response.json
    assert 'access_token' in result
    assert 'refresh_token' in result
    access_token = result['access_token']
    # проверяем, что можем войти с новым access-токеном
    response = client.post(
        path='/api/v1/login', headers={'Authorization': f'Bearer {access_token}'}
    )
    assert response.status_code == http.HTTPStatus.OK


def test_refresh_reuse_refresh_token(client, clear_db, account_temp_user, refresh_header):
    response = client.post(path='/api/v1/refresh', headers=refresh_header)
    assert response.status_code == http.HTTPStatus.OK

    response = client.post(path='/api/v1/refresh', headers=refresh_header)
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED
    response = client.post(path='/api/v1/refresh', headers=refresh_header)
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_refresh_use_access_token(client, clear_db, account_temp_user, access_header):
    response = client.post(path='/api/v1/refresh', headers=access_header)
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_refresh_invalid_header(client, clear_db, account_temp_user, valid_jwt_pair):
    response = client.post(path='/api/v1/refresh', headers={})
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED
