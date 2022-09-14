from flask_restx import reqparse

from app.settings.config import settings

authorization_parser = reqparse.RequestParser()
authorization_parser.add_argument(
    'Authorization', type=str, location='headers',
)

pagination_request_parser = authorization_parser.copy()
pagination_request_parser.add_argument(
    'page', type=int, default=settings.PAGINATION.PAGE_NUMBER, location='args'
)
pagination_request_parser.add_argument(
    'per_page', type=int, default=settings.PAGINATION.PAGE_SIZE, location='args'
)

role_request_update_parser = authorization_parser.copy()
role_request_update_parser.add_argument(
    'name', type=str, required=False, location='form',
)
role_request_update_parser.add_argument(
    'description', type=str, required=False, location='form',
)

role_request_create_parser = authorization_parser.copy()
role_request_create_parser.add_argument(
    'name', type=str, required=True, location='form',
)
role_request_create_parser.add_argument(
    'description', type=str, required=True, location='form',
)

users_ids_request_parser = authorization_parser.copy()
users_ids_request_parser.add_argument('status', action='split', location='args')
users_ids_request_parser.add_argument('roles', action='split', location='args')
