from app.api.v1.api_schemas import Params
from app.services.body_builder.base import BaseElasticBodyBuilder


class FilmElasticBodyBuilder(BaseElasticBodyBuilder):
    async def build_request_body(self, params: Params, index: str) -> dict:
        body = await super().build_request_body(params, index)
        # filter_query = params.filter_query.dict(exclude_none=True)
        # if filter_query:
        #     body.update(self._must_data)
        #     query = list()
        #     for path, idx in filter_query.items():
        #         query.append(self._get_nested_query(path, idx))
        #     body = (
        #         await self._create_genre_body(body, query)
        #         if params.filter_query.genre
        #         else await self._create_person_filter_body(body, query)
        #     )
        return body

    # async def _create_person_filter_body(self, body, query):
    #     should = self._should_data
    #     should['bool']['should'].extend(query)
    #     body['query']['bool']['must'].append(should)
    #     return body
    #
    # async def _create_genre_body(self, body, query):
    #     body['query']['bool']['must'].extend(query)
    #     return body
    #
    # @property
    # def _should_data(self):
    #     return {'bool': {'should': list()}}
    #
    # @property
    # def _must_data(self):
    #     return {'query': {'bool': {'must': []}}}
    #
    # @property
    # def _nested_data(self):
    #     return {'nested': {'query': {'bool': {'must': []}}}}
    #
    # def _get_nested_query(self, path, id):
    #     nested_q = self._nested_data
    #     res = nested_q
    #     res['nested']['path'] = path
    #     res['nested']['query']['bool']['must'].append({'match': {f'{path}.uuid': id}})
    #
    #     return res
