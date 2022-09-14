def get_response(request_method, headers, url, query_param=None, body_params=None):
    if query_param:
        params = '&'.join(f'{key}={value}' for key, value in query_param.items())
        url = f'{url}?{params}'
    return request_method(path=url, headers=headers, data=body_params or {})
