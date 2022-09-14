from contextlib import contextmanager

from postgres_to_es.settings import settings
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, declarative_base

engine = create_engine(
    f'postgresql://{settings.DB.USER}:{settings.DB.PASSWORD}@{settings.DB.HOST}:{settings.DB.PORT}/{settings.DB.DBNAME}',
    echo=True,
)
engine.connect()
session = Session(bind=engine)

meta = MetaData(schema='content')
Base = declarative_base(metadata=meta)


@contextmanager
def session_scope():
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
