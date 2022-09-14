import logging
from time import sleep

from elasticsearch.exceptions import ElasticsearchException
from postgres_to_es.etl_services.es_services import ElasticsearchService
from postgres_to_es.etl_services.etl_services import ETL
from postgres_to_es.etl_services.pg_services import PostgresConnector, PostgresCursor
from postgres_to_es.etl_services.state_service import JsonFileStorage, State
from postgres_to_es.schemes import (
    DocSchemaEnum,
    FilmworkStateSchema,
    GenreStateSchema,
    PersonStateSchema,
)
from postgres_to_es.settings import settings
from psycopg2 import DatabaseError


def main():
    # logger setting
    logger = logging.getLogger('postgres_to_es')
    logger.setLevel(settings.LOG_LEVEL)
    fh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Set keeper of the state
    state = State(JsonFileStorage())

    logger.info('*** Start migration ***')
    while True:
        logger.info('*** Open connections ***')
        indexes_names = [
            settings.ES.GENRES_INDEX_NAME,
            settings.ES.PERSONS_INDEX_NAME,
            settings.ES.FILM_WORKS_INDEX_NAME,
        ]
        es_conn = ElasticsearchService(indexes_names)
        with PostgresConnector().connection as postgres_conn:
            with PostgresCursor(connection=postgres_conn).cursor as postgres_cur:
                film_work = ETL(
                    doc_schema=DocSchemaEnum.filmwork.value,
                    state_storage=state,
                    state_schema=FilmworkStateSchema,
                    es_client=es_conn,
                    pg_conn=postgres_conn,
                    pg_curs=postgres_cur,
                )
                genre = ETL(
                    doc_schema=DocSchemaEnum.genre.value,
                    state_storage=state,
                    state_schema=GenreStateSchema,
                    es_client=es_conn,
                    pg_conn=postgres_conn,
                    pg_curs=postgres_cur,
                )
                person = ETL(
                    doc_schema=DocSchemaEnum.person.value,
                    state_storage=state,
                    state_schema=PersonStateSchema,
                    es_client=es_conn,
                    pg_conn=postgres_conn,
                    pg_curs=postgres_cur,
                )
                try:
                    film_work.run()
                    genre.run()
                    person.run()
                except (ElasticsearchException, DatabaseError) as exc_main:
                    logger.error(exc_main)
                finally:
                    logger.info('*** Close connections ***')
                    es_conn.client.transport.close()
                logger.info('Sleep for %s seconds', settings.APP.SLEEP_TIMEOUT)
                sleep(settings.APP.SLEEP_TIMEOUT)


if __name__ == '__main__':
    main()
