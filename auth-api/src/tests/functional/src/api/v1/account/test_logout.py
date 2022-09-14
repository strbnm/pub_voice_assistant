import http


def test_logout_ok(client, clear_db, account_temp_user, access_header):
    response = client.post(path='/api/v1/logout', headers=access_header)
    assert response.status_code == http.HTTPStatus.OK


def test_logout_with_twin_used_same_access_token(
    client, clear_db, account_temp_user, access_header, valid_jwt_pair
):
    response = client.post(path='/api/v1/logout', headers=access_header)
    assert response.status_code == http.HTTPStatus.OK
    response = client.post(path='/api/v1/logout', headers=access_header)
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED
