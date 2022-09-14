import http


def test_rate_limit_ok(client, account_temp_user, access_header):
    response = client.post(path='/api/v1/login', headers=access_header)
    assert response.status_code == http.HTTPStatus.OK

    for _ in range(100):
        response = client.post(path='/api/v1/login', headers=access_header)

    assert response.status_code == http.HTTPStatus.TOO_MANY_REQUESTS
