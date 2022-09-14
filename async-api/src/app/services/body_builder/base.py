import logging

from app.api.v1.api_schemas import Params
from app.services.body_builder.abstract import SearchBodyBuilder
from app.services.controllers.base import IndexEnum
from elasticsearch_dsl import Search, Q

logger = logging.getLogger(__name__)


class BaseElasticBodyBuilder(SearchBodyBuilder):
    async def build_request_body(self, params: Params, index: str) -> dict:
        logger.info('params: %s, index: %s', params, index)
        body = Search(index=index).sort(params.sort_field)
        if params.query and index == IndexEnum.MOVIES.value:
            body = body.query(
                Q(
                    'bool',
                    must=[
                        Q(
                            'multi_match',
                            query=params.query,
                            fields=['title', 'title_ru'],
                            operator='and',
                            fuzziness='AUTO',
                        )
                    ],
                )
            )
        elif params.query and index == IndexEnum.PERSONS.value:
            body = body.query(
                Q(
                    'bool',
                    must=[
                        Q(
                            'multi_match',
                            query=params.query,
                            fields=['full_name', 'full_name_ru'],
                            operator='and',
                            fuzziness='AUTO',
                        )
                    ],
                )
            )
        elif params.query and index == IndexEnum.GENRES.value:
            body = body.query(
                Q('bool', must=[Q('query_string', default_field='name', query=params.query)])
            )
        elif params.filter_query.genre:
            genre_id = params.filter_query.genre
            body = body.query(
                Q(
                    'bool',
                    must=[
                        Q(
                            'nested',
                            path='genre',
                            query=Q('bool', must=Q('match', genre__uuid=genre_id)),
                        )
                    ],
                )
            )
        elif params.filter_query.person:
            person_id = params.filter_query.person
            roles = list()
            for role in ('directors', 'actors', 'writers'):
                roles.append(
                    Q(
                        'nested',
                        path=role,
                        query=Q('bool', must=Q('match', **{f'{role}.uuid': person_id})),
                    )
                )
            body = body.query('bool', must=Q('bool', should=roles))

        if params.is_subscriber is False and index == IndexEnum.MOVIES.value:
            body = body.filter('term', subscription_required='false')
        result = body.to_dict()
        logger.info('Запрос в ES: %s', result)
        return result
