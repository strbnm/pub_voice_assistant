from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore

from app.database import db
from app.models.roles import Role
from app.models.user import User

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()


def init_datastore(app: Flask):
    security.init_app(app, user_datastore)
