from flask_restx import inputs

from app.api.v1.account import namespace
from app.settings.config import settings

pattern = r'(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{8,}'

authorization_parser = namespace.parser()
authorization_parser.add_argument(
    'Authorization', type=str, location='headers',
)

signup_request_parser = namespace.parser()
signup_request_parser.add_argument(
    'username', type=str, required=True, location='form',
)
signup_request_parser.add_argument(
    'password', type=inputs.regex(pattern=pattern), required=True, location='form',
)
signup_request_parser.add_argument(
    'email', type=inputs.email(), required=True, location='form'
)
signup_request_parser.add_argument(
    'first_name', type=str, location='form',
)
signup_request_parser.add_argument(
    'last_name', type=str, location='form',
)

login_request_parser = authorization_parser.copy()
login_request_parser.add_argument(
    'login', type=inputs.email(), required=True, location='form',
)
login_request_parser.add_argument(
    'password', type=str, required=True, location='form',
)


user_password_update_request_parser = authorization_parser.copy()
user_password_update_request_parser.add_argument(
    'old_password', type=str, required=True, location='form',
)
user_password_update_request_parser.add_argument(
    'new_password', type=inputs.regex(pattern=pattern), required=True, location='form',
)

history_request_parser = authorization_parser.copy()
history_request_parser.add_argument(
    'page', type=int, default=settings.PAGINATION.PAGE_NUMBER, location='args'
)
history_request_parser.add_argument(
    'per_page', type=int, default=settings.PAGINATION.PAGE_SIZE, location='args'
)
confirm_email_request_parser = authorization_parser.copy()
