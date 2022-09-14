from flask_restx import fields
from pydantic import BaseModel

from app.api.v1.account import namespace

signup_response = namespace.model(
    'SignupUserResponse',
    {
        'id': fields.String,
        'username': fields.String,
        'email': fields.String,
        'first_name': fields.String,
        'last_name': fields.String,
        'is_active': fields.Boolean,
        'created_at': fields.DateTime,
    },
)

user_history_response = namespace.model(
    'History',
    {
        'id': fields.String,
        'user_id': fields.String,
        'timestamp': fields.DateTime,
        'user_agent': fields.String,
        'ip_addr': fields.String,
        'device': fields.String,
        'platform': fields.String,
    },
)

account_paginator_response = namespace.model(
    'Account_Paginator',
    {
        'count': fields.Integer,
        'total_pages': fields.Integer,
        'prev': fields.Integer,
        'next': fields.Integer,
        'results': fields.Nested(user_history_response),
    },
)


class LogInArgs(BaseModel):
    login: str
    password: str


class PasswordArgs(BaseModel):
    old_password: str
    new_password: str
