import logging
from contextlib import contextmanager

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from app.settings.config import settings

logger = logging.getLogger(__name__)

# Задаем шаблон наименования индексов и constraint’ов по умолчанию
convention = {
    'all_column_names': lambda constraint, table: '_'.join(
        [column.name for column in constraint.columns.values()]
    ),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uk': 'uk__%(table_name)s__%(all_column_names)s',
    'ck': 'uk__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__' '%(referred_table_name)s',
    'pk': 'pk__%(table_name)s',
}

meta = MetaData(schema=settings.DB.SCHEMA, naming_convention=convention)

db = SQLAlchemy(metadata=meta)
migrate = Migrate()


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DB.DSN
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger.debug('Строка подключения к DB: %s', settings.DB.DSN)
    db.init_app(app)
    migrate.init_app(app, db)


@contextmanager
def session_scope():
    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
