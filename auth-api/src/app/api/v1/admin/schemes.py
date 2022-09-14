from typing import Optional

from flask_restx import fields
from pydantic import BaseModel

from app.api.v1.admin import roles_namespace, users_namespace

role = {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String,
}

roles_role_schema = roles_namespace.model('Role', role,)

users_role_schema = users_namespace.model('Role', role,)

users_paginator_response = users_namespace.model(
    'Users_Paginator',
    {
        'count': fields.Integer,
        'total_pages': fields.Integer,
        'prev': fields.Integer,
        'next': fields.Integer,
        'results': fields.Nested(users_role_schema),
    },
)

roles_paginator_response = roles_namespace.model(
    'Roles_Paginator',
    {
        'count': fields.Integer,
        'total_pages': fields.Integer,
        'prev': fields.Integer,
        'next': fields.Integer,
        'results': fields.Nested(roles_role_schema),
    },
)


class RoleItem(BaseModel):
    name: Optional[str]
    description: Optional[str]


userinfo_response = users_namespace.model(
    'Userinfo',
    {
        'id': fields.String,
        'username': fields.String,
        'email': fields.String,
        'first_name': fields.String,
        'last_name': fields.String,
    },
)

users_ids_response = users_namespace.model('Users_Ids', {'id': fields.String})

user_id = {
    'id': fields.String,
}

users_ids_schema = users_namespace.model('Users_Ids', user_id)
