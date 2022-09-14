from flask_restx import Namespace

roles_namespace = Namespace(
    'Admin_roles', path='/api/v1/roles', description='API для управления ролями'
)
users_namespace = Namespace(
    'Admin_users', path='/api/v1/users', description='API для управления доступами'
)

from app.api.v1.admin import roles, users  # noqa
