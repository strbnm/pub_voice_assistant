import logging
from logging import config as logging_config
from urllib.parse import quote_plus as quote

import backoff
import uvicorn as uvicorn
from aiohttp import ClientSession
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError

from app.api.v1 import voice_assistant
from app.core.backoff_handler import backoff_hdlr, backoff_hdlr_success
from app.core.config import settings
from app.core.logger import LOGGING
from app.core.session import get_session
from app.jaeger_service import init_tracer

logging_config.dictConfig(LOGGING)

app = FastAPI(
    title=settings.APP.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    redoc_url='/api/redoc',
    default_response_class=ORJSONResponse,
)

init_tracer(app)

url = 'mongodb://{user}:{pw}@{hosts}/?replicaSet={rs}&authSource={auth_src}'.format(
    user=quote(settings.MONGO.DB_USER),
    pw=quote(settings.MONGO.DB_PASS),
    hosts=settings.MONGO.DB_HOSTS,
    rs=settings.MONGO.DB_RS,
    auth_src=settings.MONGO.DB_NAME,
)


@app.on_event('startup')
async def startup():
    app.mongodb_client = backoff.on_exception(
        wait_gen=backoff.expo,
        max_tries=settings.BACKOFF.RETRIES,
        max_time=settings.BACKOFF.MAX_TIME,
        exception=PyMongoError,
        on_backoff=backoff_hdlr,
        on_success=backoff_hdlr_success,
    )(AsyncIOMotorClient)(url, tlsCAFile=settings.MONGO.CACERT)

    app.mongodb = app.mongodb_client[settings.MONGO.DB_NAME]

    app.state.session = await get_session()


@app.on_event('shutdown')
async def shutdown():
    app.mongodb_client.close()
    session: ClientSession = app.state.session
    await session.close()


app.include_router(
    voice_assistant.router, prefix='/api/v1', tags=['Голосовой помощник'],
)


if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8001, log_config=LOGGING, log_level=logging.INFO,
    )
