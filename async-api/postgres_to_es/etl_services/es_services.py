import json
import logging
import os
from typing import Optional

from elasticsearch import Elasticsearch, ElasticsearchException
from elasticsearch.helpers import bulk
from postgres_to_es.etl_services.backoff_service import backoff
from postgres_to_es.schemes import DocSchemaEnum
from postgres_to_es.settings import settings

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Class to work with Elasticsearch engine"""

    @backoff(
        logger=logger,
        verbose_name='ElasticsearchService.__init__()',
        max_attempt=settings.BACKOFF.MAX_ATTEMPT,
        exception=ElasticsearchException,
    )
    def __init__(self, indexes_names: list):
        self.client = Elasticsearch(hosts=f'{settings.ES.HOST}:{settings.ES.PORT}')
        self.indexes_names = indexes_names
        index_files_names = [
            ''.join([i_name, settings.ES.INDEX_SCHEMA_FILE_SUFFIX])
            for i_name in self.indexes_names
        ]
        self.files_path = [
            os.path.join(settings.ES.INDEX_SCHEMA_PATH, index_file_name)
            for index_file_name in index_files_names
        ]
        for index, file_path in zip(self.indexes_names, self.files_path):
            if not self.client.indices.exists(index=index):
                self.create_index(index=index, file_path=file_path)
                logger.info('Index "%s" successfully created!', index)

    @backoff(
        logger=logger,
        verbose_name='ElasticsearchService.create_index()',
        max_attempt=settings.BACKOFF.MAX_ATTEMPT,
        exception=ElasticsearchException,
    )
    def create_index(
        self, index: str, file_path: str, ignore_http_response: int = 400
    ) -> None:
        with open(file_path, 'r', encoding='UTF8') as index_schema_file:
            index_settings = json.load(index_schema_file)
            self.client.indices.create(
                index=index, **index_settings, ignore=ignore_http_response
            )

    @backoff(
        logger=logger,
        verbose_name='ElasticsearchService.migrate_data()',
        max_attempt=settings.BACKOFF.MAX_ATTEMPT,
        exception=ElasticsearchException,
    )
    def migrate_data(self, actions: dict, doc_schema: DocSchemaEnum) -> None:
        if not actions:
            return
        index_name = self.get_index_by_schema(doc_schema)
        lines, status = bulk(
            client=self.client,
            actions=(
                {'_index': index_name, '_id': action.get('uuid'), **action}
                for action in actions
            ),
        )
        if not status:
            logger.info('Successful migrate data: %s', lines)
        else:
            logger.info(
                'Successful migrate data: %s\nUnsuccessful migrate data and list error: %s',
                lines,
                status,
            )

    @staticmethod
    def get_index_by_schema(doc_schema: DocSchemaEnum) -> Optional[str]:
        index_resolver = {
            DocSchemaEnum.filmwork.value: settings.ES.FILM_WORKS_INDEX_NAME,
            DocSchemaEnum.person.value: settings.ES.PERSONS_INDEX_NAME,
            DocSchemaEnum.genre.value: settings.ES.GENRES_INDEX_NAME,
        }
        if doc_schema not in index_resolver:
            return None
        return index_resolver[doc_schema]
