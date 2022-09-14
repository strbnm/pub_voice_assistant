from flask_restx import Namespace

namespace = Namespace(
    'Account', path='/api/v1', description='API для сайта и личного кабинета'
)

from app.api.v1.account import account, oauth, profiles  # noqa
