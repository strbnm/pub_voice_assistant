import logging

from app.api.v1.api_schemas import Params
from app.models.persons import ESPerson
from app.services.controllers.base import BaseService, IndexEnum

logger = logging.getLogger(__name__)


class PersonService(BaseService):
    index = IndexEnum.PERSONS.value
    model = ESPerson

    def get_cache_key(self, params: Params):
        args = [
            self.index,
            params.query,
            params.sort_field,
            params.pagination.offset,
            params.pagination.limit,
            params.filter_query.person,
        ]
        logger.debug('PersonService cache key: %s', ':::'.join(str(i) for i in args))
        return ':::'.join(str(i) for i in args)
