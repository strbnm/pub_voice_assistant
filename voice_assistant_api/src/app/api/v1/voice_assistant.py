import collections
from typing import Awaitable

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from starlette.background import BackgroundTasks
from starlette.requests import Request

from app.services.alice_voice_assistant import (
    AliceVoiceAssistantService,
    get_alice_voice_assistant_service,
)
from app.services.save_to_mongodb import save_doc

router = APIRouter()


@router.post(
    '/voice_assistant',
    summary='Webhook для Яндекс.Алисы',
    description='Backend для запросов от Яндекс.Алисы',
)
async def get_movies_info(
    request: Request,
    background_tasks: BackgroundTasks,
    alice_service: Awaitable[AliceVoiceAssistantService] = Depends(
        get_alice_voice_assistant_service
    ),
) -> ORJSONResponse:
    if isinstance(alice_service, collections.Awaitable):
        alice_service = await alice_service
    event: dict = await request.json()
    response, collection = await alice_service.handler(request_body=event)
    background_tasks.add_task(save_doc, request, event, response, collection)

    return ORJSONResponse(content=response)
