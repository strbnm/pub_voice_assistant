import logging
from functools import lru_cache
from typing import Any

from fastapi import Depends

from app.services.alice.request import AliceRequest
from app.services.alice.scenes import DEFAULT_SCENE, SCENES
from app.services.alice.state import STATE_REQUEST_KEY
from app.services.alice_voice_assistant_abstract import VoiceAssistantAbstractService
from app.services.movies_data_search import get_movies_data_search, MoviesDataSearch

logger = logging.getLogger(__name__)


class AliceVoiceAssistantService(VoiceAssistantAbstractService):
    def __init__(self, search_service: MoviesDataSearch) -> None:
        self.search_service = search_service

    async def handler(self, request_body: dict[str, Any]) -> tuple[dict[str, Any], str]:
        alice_request = AliceRequest(
            request_body=request_body, search_service=self.search_service
        )
        current_scene_id = (
            request_body.get('state', {}).get(STATE_REQUEST_KEY, {}).get('scene')
        )

        if current_scene_id is None:
            collection = 'alice_response'
            return await DEFAULT_SCENE().reply(alice_request), collection

        current_scene = SCENES.get(current_scene_id, DEFAULT_SCENE)()
        next_scene = current_scene.move(alice_request)

        if next_scene is not None:
            response: dict = await next_scene.reply(alice_request)
            logger.debug('Response from scene [%s]: %s', next_scene, response)
            collection = 'alice_response'
            return response, collection
        else:
            fallback_response = await current_scene.fallback(alice_request)
            logger.debug(
                'Fallback response from scene [%s]: %s', next_scene, fallback_response
            )
            collection = 'alice_fallback_request'
            return fallback_response, collection


@lru_cache()
async def get_alice_voice_assistant_service(
    search_service: MoviesDataSearch = Depends(get_movies_data_search),
) -> AliceVoiceAssistantService:
    return AliceVoiceAssistantService(search_service=search_service)
