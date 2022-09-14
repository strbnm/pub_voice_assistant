import logging
from abc import abstractmethod
from json import loads
from typing import Any, Callable, Generator, Optional, Tuple, Union

from postgres_to_es.etl_services.es_services import ElasticsearchService
from postgres_to_es.etl_services.pg_services import (
    PostgresConnector,
    PostgresCursor,
    PostgresExtract,
)
from postgres_to_es.etl_services.state_service import State
from postgres_to_es.schemes import (
    DocSchemaEnum,
    ESBaseSchema,
    FilmworkStateSchema,
    GenreStateSchema,
    PersonStateSchema,
)
from postgres_to_es.settings import settings
from psycopg2.extras import DictRow

logger = logging.getLogger(__name__)


class BaseETL:
    @abstractmethod
    async def run(self, *args, **kwargs) -> None:
        """Main process ETL: extract -> transform -> load"""
        pass

    @abstractmethod
    async def extract(self, *args, **kwargs) -> PostgresExtract:
        """Extract film work data from Postgresql"""
        pass

    @abstractmethod
    async def transform(self, *args, **kwargs) -> dict[str, ESBaseSchema]:
        """Transform extracted data and prepare to load to ElasticSearch"""
        pass

    @abstractmethod
    async def load(self, *args, **kwargs) -> None:
        """Load film work data to indexes ElasticSearch"""
        pass


class ETLError(Exception):
    pass


class ETL(BaseETL):
    def __init__(
        self,
        doc_schema: DocSchemaEnum,
        state_storage: State,
        state_schema: Union[GenreStateSchema, FilmworkStateSchema, PersonStateSchema],
        es_client: ElasticsearchService,
        pg_conn: PostgresConnector,
        pg_curs: PostgresCursor,
    ) -> None:
        self.doc_schema = doc_schema
        self.state_storage = state_storage
        self.es_client = es_client
        self.state_schema = state_schema
        self.conn = pg_conn
        self.cursor = pg_curs

    def run(self) -> None:
        """
        Run ETL process: extract -> transform -> load
        """
        logger.info('Begin ETL with schema %s', self.doc_schema.__name__)

        try:
            db_result, status = self.extract()
            if not db_result:
                logger.info(
                    'No updated data for ETL with schema %s.', self.doc_schema.__name__
                )
                return
            for chunk in self.get_chunk(db_result):
                self.transform_and_load(chunk=chunk)
        except Exception as err:
            raise ETLError from err
        status.flag_ETL_success = True
        state = status.json()
        self.state_storage.set_state(self.doc_schema.__name__, state)

        logger.info('ETL with schema %s successfully done!', self.doc_schema.__name__)

    def extract(
        self,
    ) -> Tuple[list[DictRow], Union[GenreStateSchema, FilmworkStateSchema, PersonStateSchema]]:
        """
        Fetch last changes from multiple DB tables with one query.
        """
        state = self.state_storage.get_state(self.doc_schema.__name__)
        if state is None:
            status = self.state_schema()
        else:
            status = self.state_schema(
                **loads(self.state_storage.get_state(self.doc_schema.__name__))
            )
        extractor = get_db_extractor(self.doc_schema)

        logger.debug('Data extraction for schema %s started.', self.doc_schema.__name__)

        db_result, new_status = extractor(self.cursor, status)
        return db_result, new_status

    @staticmethod
    def get_chunk(db_result: list[DictRow]) -> Generator[list[DictRow], None, None]:
        """
        Drain chunked data from DB cursor with settings.ETL.CHUNK_SIZE.
        """
        if not db_result:
            return
        chunk: list[DictRow] = []
        for row in db_result:
            if len(chunk) == settings.ETL.CHUNK_SIZE:
                yield chunk
                chunk = []
            chunk.append(row)
        yield chunk

    def transform_and_load(self, chunk: list[DictRow]) -> None:
        """
        Transform db data and load it to elasticsearch.
        """
        if not chunk:
            return
        logger.debug(
            'Ready to process %s rows, schema %s', len(chunk), self.doc_schema.__name__
        )
        transformed_data = self.transform(chunk)
        self.load(transformed_data)

    def transform(self, chunk: list[DictRow]) -> Generator[Any, Any, None]:
        for num, row in enumerate(chunk, start=1):
            logger.debug('Record #%s for load to ES: %s', num, dict(row))
        return (self.doc_schema(**dict(row)).dict() for row in chunk)

    def load(self, transformed_data) -> None:
        """load data to elasticsearch."""
        if not transformed_data:
            return
        try:
            self.es_client.migrate_data(transformed_data, self.doc_schema)
        except Exception as err:
            logger.exception('Load data to es failed!')
            raise ETLError from err


def extract_all_film_works(
    pg_cursor: PostgresExtract, status: FilmworkStateSchema
) -> tuple[Generator, FilmworkStateSchema]:
    db_result, status.filmwork_updated_at = pg_cursor.get_all_film_works()
    _, status.genre_updated_at = pg_cursor.get_last_update_genre_id()
    _, status.person_updated_at = pg_cursor.get_last_update_person_id()
    return db_result, status


def extract_chunk_updated_film_works(
    pg_cursor: PostgresExtract, status: FilmworkStateSchema
) -> Union[tuple[list, FilmworkStateSchema], tuple[Optional[Generator], FilmworkStateSchema]]:
    fw_id_by_persons: list[str] = []
    fw_id_by_genres: list[str] = []
    new_status = FilmworkStateSchema()
    # get film works id by persons
    persons_id, new_status.person_updated_at = pg_cursor.get_persons_id()
    if persons_id:
        fw_id_by_persons = pg_cursor.get_film_works_id_by_persons(persons_id=persons_id)
    # get film works id by genres
    genres_id, new_status.genre_updated_at = pg_cursor.get_genres_id()
    if genres_id:
        fw_id_by_genres = pg_cursor.get_film_works_id_by_genres(genres_id=genres_id)
    # get film works id
    film_works_id, new_status.filmwork_updated_at = pg_cursor.get_film_works_id()
    if not any(
        [
            new_status.person_updated_at,
            new_status.genre_updated_at,
            new_status.filmwork_updated_at,
        ]
    ):
        return [], status
    all_film_works_id = set(film_works_id + fw_id_by_persons + fw_id_by_genres)
    status.filmwork_updated_at = new_status.filmwork_updated_at
    status.genre_updated_at = new_status.genre_updated_at
    status.person_updated_at = new_status.genre_updated_at
    db_result = pg_cursor.get_film_works_by_ids(film_works_ids=tuple(all_film_works_id))
    return db_result, status


def get_film_works(
    pg_cursor: PostgresCursor, status: FilmworkStateSchema
) -> tuple[Union[Optional[Generator], list], FilmworkStateSchema]:
    """Function get cursor with all updated filmwork"""
    pg_cursor = PostgresExtract(cursor=pg_cursor, state=status)
    # if this is first load data from Postgresql to ElasticSearch, then load all film_work with related data
    if not status.flag_ETL_success:
        return extract_all_film_works(pg_cursor=pg_cursor, status=status)
    # otherwise, select the updated data and upload it to ElasticSearch
    else:
        return extract_chunk_updated_film_works(pg_cursor=pg_cursor, status=status)


def get_persons(
    pg_cursor: PostgresCursor, status: PersonStateSchema
) -> tuple[Union[Generator, list], PersonStateSchema]:
    """Function get cursor with all updated persons"""
    pg_cursor = PostgresExtract(cursor=pg_cursor, state=status)
    db_result, status.person_updated_at = pg_cursor.get_persons()
    return db_result, status


def get_genres(
    pg_cursor: PostgresCursor, status: GenreStateSchema
) -> tuple[Union[Generator, list], GenreStateSchema]:
    """Function get cursor with all updated persons"""
    pg_cursor = PostgresExtract(cursor=pg_cursor, state=status)
    db_result, status.genre_updated_at = pg_cursor.get_genres()
    return db_result, status


def get_db_extractor(doc_schema: DocSchemaEnum) -> Optional[Callable]:
    extractor_resolver = {
        DocSchemaEnum.filmwork.value: get_film_works,
        DocSchemaEnum.person.value: get_persons,
        DocSchemaEnum.genre.value: get_genres,
    }
    if doc_schema not in extractor_resolver:
        return None
    extractor = extractor_resolver[doc_schema]
    return extractor
