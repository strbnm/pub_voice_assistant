import logging
from typing import Generator, Optional, Tuple, Union

import psycopg2
from postgres_to_es.etl_services.backoff_service import backoff
from postgres_to_es.queries import (
    query_all_film_works_id,
    query_film_works_by_genres,
    query_film_works_by_ids,
    query_film_works_by_persons,
    query_genres_by_ids,
    query_last_updated_genre,
    query_last_updated_person,
    query_persons_by_ids,
    query_updated_film_works,
    query_updated_genres,
    query_updated_persons,
)
from postgres_to_es.schemes import FilmworkStateSchema, GenreStateSchema, PersonStateSchema
from postgres_to_es.settings import settings
from psycopg2 import DatabaseError
from psycopg2.extensions import connection as pg_connection
from psycopg2.extras import DictCursor

logger = logging.getLogger(__name__)


class PostgresCursor:
    """Class for work with Postgresql DictCursor"""

    def __init__(self, connection: pg_connection):
        self._cursor: Optional[DictCursor] = None
        self._connection = connection

    @property
    def cursor(self) -> DictCursor:
        """Check cursor, if closed, recreate database cursor and return"""
        if self._cursor and not self._cursor.closed:
            cursor = self._cursor
        else:
            cursor = self.create_cursor()
        return cursor

    @backoff(
        logger=logger,
        verbose_name='PostgresCursor.create cursor()',
        max_attempt=settings.BACKOFF.MAX_ATTEMPT,
        exception=DatabaseError,
    )
    def create_cursor(self) -> DictCursor:
        """Create Postgres cursor"""
        return self._connection.cursor()


class PostgresConnector:
    """Class to work with Postgresql Database"""

    def __init__(self, pg_settings=settings.DB.DSN):
        self.dsl: dict = dict(pg_settings)
        self.conn: Optional[pg_connection] = None

    @property
    def connection(self):
        """Check connection, if closed, reconnect to DB and return"""
        if self.conn and not self.conn.closed:
            conn = self.conn
        else:
            conn = self.create_conn()
        return conn

    @backoff(
        logger=logger,
        verbose_name='PostgresConnector.create_conn()',
        max_attempt=settings.BACKOFF.MAX_ATTEMPT,
        exception=DatabaseError,
    )
    def create_conn(self) -> pg_connection:
        """Create connection with Postgres"""
        return psycopg2.connect(**self.dsl, cursor_factory=DictCursor)


class PostgresExtract:
    """The main class of interaction with the PostgreSQL database"""

    def __init__(
        self,
        cursor: PostgresCursor,
        state: Union[GenreStateSchema, FilmworkStateSchema, PersonStateSchema],
    ):
        """
        Init cursor and keeper of the state
        """
        self.cur = cursor
        self.state = state

    def query_executor(self, query):
        """Return result of executed database query"""
        try:
            self.cur.execute(query)
            return self.cur.fetchall()
        except DatabaseError:
            logger.error('DatabaseError exception occurred', exc_info=True)

    def query_batch_executor(self, query) -> Generator:
        """Return result of executed database query as generator"""
        try:
            self.cur.execute(query)
        except DatabaseError:
            logger.error('DatabaseError exception occurred', exc_info=True)
        while True:
            rows = self.cur.fetchmany(size=settings.ETL.LIMIT_READ_RECORD_DB)
            if not rows:
                break
            yield from rows

    def get_all_film_works(self) -> Tuple[Generator, str]:
        """Return db cursor on result query all film_works and related data and last updated_at film_work"""
        film_works = self.query_executor(query=query_all_film_works_id())
        if film_works:
            film_works_ids = tuple([film_work['id'] for film_work in film_works])
            db_result = self.query_batch_executor(
                query=query_film_works_by_ids(film_works_id=film_works_ids)
            )
            film_work_status = str(film_works[-1].get(settings.ETL.STATE_FIELD))
            return db_result, film_work_status

    def get_film_works_by_ids(self, film_works_ids: Tuple[str]) -> Optional[Generator]:
        """Return db cursor on result query all film_works and related data and last updated_at film_work"""
        if film_works_ids:
            db_result = self.query_batch_executor(
                query=query_film_works_by_ids(film_works_id=film_works_ids)
            )
            return db_result

    def get_persons(self) -> Tuple[Union[Generator, list], Optional[str]]:
        """Return db cursor on result query all persons and related data and last updated_at person"""
        updated_at = self.state.person_updated_at
        chunk_persons = self.query_batch_executor(query=query_updated_persons(updated_at))
        persons = []
        for row in chunk_persons:
            if not row:
                break
            persons.append(row)
        if persons:
            persons_ids = tuple([person['id'] for person in persons])
            db_result = self.query_batch_executor(
                query=query_persons_by_ids(persons_ids=persons_ids)
            )
            person_status = str(persons[-1].get(settings.ETL.STATE_FIELD))
            return db_result, person_status
        return [], None

    def get_genres(self) -> Tuple[Union[Generator, list], Optional[str]]:
        """Return db cursor on result query all genres and related data and last updated_at genres"""
        updated_at = self.state.genre_updated_at
        chunk_genres = self.query_batch_executor(query=query_updated_genres(updated_at))
        genres = []
        for row in chunk_genres:
            if not row:
                break
            genres.append(row)
        if genres:
            genres_ids = tuple([genre['id'] for genre in genres])
            db_result = self.query_batch_executor(
                query=query_genres_by_ids(genres_ids=genres_ids)
            )
            person_status = str(genres[-1].get(settings.ETL.STATE_FIELD))
            return db_result, person_status
        return [], None

    def get_film_works_id(self) -> tuple[list[str], Optional[str]]:
        """Return list of film_works id [id1, id2, ... idN] and last updated_at selection as str"""
        # get state
        updated_at = self.state.filmwork_updated_at
        # get film_works id
        # since only the index and the update date are obtained from the database and
        # the SQL query has a limit on the number of half-time records (LIMIT {pg_config.limit}),
        # we use function query_executor with cursor.fetchall() to load
        film_works = self.query_executor(
            query=query_updated_film_works(datetime_value=updated_at)
        )
        if film_works:
            return (
                [film_work['id'] for film_work in film_works],
                str(film_works[-1].get(settings.ETL.STATE_FIELD)),
            )
        return [], None

    def get_persons_id(self) -> tuple[list[str], Optional[str]]:
        """Return list of persons id and last updated_at selection"""
        # get state
        updated_at = self.state.person_updated_at
        # get persons id
        # since only the index and the update date are obtained from the database and
        # the SQL query has a limit on the number of half-time records (LIMIT {pg_config.limit}),
        # we use function query_executor with cursor.fetchall() to load
        persons = self.query_executor(query=query_updated_persons(datetime_value=updated_at))
        if persons:
            return (
                [person['id'] for person in persons],
                str(persons[-1].get(settings.ETL.STATE_FIELD)),
            )
        return [], None

    def get_last_update_person_id(self) -> tuple[str, str]:
        """Return last updated person (id, updated_at)"""
        # get last updated person
        last_updated_persons = self.query_executor(query=query_last_updated_person())
        return last_updated_persons[0]['id'], str(last_updated_persons[0]['updated_at'])

    def get_genres_id(self) -> tuple[list[str], Optional[str]]:
        """Return list of list genres id and last updated_at selection"""
        # get state
        updated_at = self.state.genre_updated_at
        # get genres id
        # since only the index and the update date are obtained from the database and
        # the SQL query has a limit on the number of half-time records (LIMIT {pg_config.limit}),
        # we use function query_executor with cursor.fetchall() to load
        genres = self.query_executor(query=query_updated_genres(datetime_value=updated_at))
        if genres:
            return (
                [genre['id'] for genre in genres],
                str(genres[-1].get(settings.ETL.STATE_FIELD)),
            )
        return [], None

    def get_last_update_genre_id(self) -> tuple[str, str]:
        """Return last updated person (id, updated_at)"""
        # get last updated genre
        last_updated_genre = self.query_executor(query=query_last_updated_genre())
        return last_updated_genre[0]['id'], str(last_updated_genre[0]['updated_at'])

    def get_film_works_id_by_persons(self, persons_id: list[str]) -> list[str]:
        """Return list of film_works id for specified persons id"""
        # get person's film works id
        film_works_by_persons = self.query_batch_executor(
            query=query_film_works_by_persons(persons_id=persons_id)
        )
        return [film_works_by_person['id'] for film_works_by_person in film_works_by_persons]

    def get_film_works_id_by_genres(self, genres_id: list[str]) -> list[str]:
        """Return list of film_works id for specified genres id"""
        # get genre's film works id
        film_works_by_genres = self.query_batch_executor(
            query=query_film_works_by_genres(genres_id=genres_id)
        )
        return [film_works_by_genre['id'] for film_works_by_genre in film_works_by_genres]
