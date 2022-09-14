from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from sqlalchemy_service import Base


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    name = Column(String(255))
    description = Column(String(), nullable=True)
    created_at = Column(DateTime(), default=datetime.now)
    updated_at = Column(DateTime(), default=datetime.now(), onupdate=datetime.now())

    def __str__(self):
        return self.name


class Person(Base):
    __tablename__ = 'person'

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    full_name = Column(String(255))
    full_name_ru = Column(String(255))
    birth_date = Column(Date(), nullable=True)
    created_at = Column(DateTime(), default=datetime.now)
    updated_at = Column(DateTime(), default=datetime.now(), onupdate=datetime.now())

    def __str__(self):
        return self.full_name


class RoleType(Enum):
    DIRECTOR = 'director'
    ACTOR = 'actor'
    WRITER = 'writer'


class FilmworkPerson(Base):
    __tablename__ = 'person_film_work'
    __table_args__ = (
        UniqueConstraint(
            'film_work_id', 'person_id', 'role', name='unique_role_person_film_work'
        ),
    )

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    film_work = Column(
        'film_work_id', UUID(as_uuid=True), ForeignKey('film_work.id', ondelete='CASCADE')
    )
    person = Column(
        'person_id', UUID(as_uuid=True), ForeignKey('person.id', ondelete='CASCADE')
    )
    role = Column(ENUM(RoleType))
    created_at = Column(DateTime(), default=datetime.now)


class FilmworkGenre(Base):
    __tablename__ = 'genre_film_work'
    __table_args__ = (
        UniqueConstraint('film_work_id', 'genre_id', name='unique_genre_film_work'),
    )

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    film_work = Column(
        'film_work_id', UUID(as_uuid=True), ForeignKey('film_work.id', ondelete='CASCADE')
    )
    genre = Column('genre_id', UUID(as_uuid=True), ForeignKey('genre.id', ondelete='CASCADE'))
    created_at = Column(DateTime(), default=datetime.now)


class FilmworkType(Enum):
    MOVIE = 'movie'
    TV_SHOW = 'tv_show'


class Filmwork(Base):
    __tablename__ = 'film_work'

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    title = Column(String(255))
    title_ru = Column(String(255))
    description = Column(Text(), nullable=True)
    description_ru = Column(Text(), nullable=True)
    creation_date = Column(Date(), nullable=True)
    subscription_required = Column(Boolean(), nullable=True)
    certificate = Column(Text(), nullable=True)
    file_path = Column(Text(), nullable=True)
    rating = Column(Float(), nullable=True)
    type = Column(String(20))
    genres = relationship('FilmworkGenre', backref='filmwork')
    persons = relationship('FilmworkPerson', backref='filmwork')
    created_at = Column(DateTime(), default=datetime.now)
    updated_at = Column(DateTime(), default=datetime.now(), onupdate=datetime.now())

    def __str__(self):
        return self.title
