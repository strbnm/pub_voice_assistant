from flask import Flask
from flask_restx import Api

from app.api.v1.account import namespace as api_v1_account_namespace
from app.api.v1.admin import roles_namespace as api_v1_roles_namespace
from app.api.v1.admin import users_namespace as api_v1_users_namespace

api = Api(title='Auth API Team8', version='1.0.0', description='Auth API service')

api.add_namespace(api_v1_account_namespace)
api.add_namespace(api_v1_roles_namespace)
api.add_namespace(api_v1_users_namespace)


def init_api(app: Flask):
    app.config['RESTX_MASK_SWAGGER'] = False
    api.init_app(app)
