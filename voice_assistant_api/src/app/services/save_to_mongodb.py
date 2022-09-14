import logging
from typing import Any

from pymongo import WriteConcern
from starlette.requests import Request

logger = logging.getLogger(__name__)


async def save_doc(
    request: Request, event: dict[str, Any], response: dict[str, Any], collection: str
) -> None:
    if not request.app.mongodb:
        return
    resp_with_request = response.copy()
    resp_with_request.update(event)
    save_request = await (
        request.app.mongodb[collection]
        .with_options(write_concern=WriteConcern(w='majority'))
        .insert_one(resp_with_request)
    )
    if save_request.acknowledged:
        logger.info(
            'Save in collection [%s] MongoDB with ObjectId [%s] response %s to the request %s',
            collection,
            save_request.inserted_id,
            response,
            event,
        )
