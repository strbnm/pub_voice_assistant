import logging
from logging import config as logging_config

import aioredis
import backoff
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse

from app.api.v1 import films, genres, persons
from app.core import dependencies
from app.core.backoff_handler import backoff_hdlr, backoff_hdlr_success
from app.core.config import settings
from app.core.logger import LOGGING
from app.core.oauth import decode_jwt
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


@app.on_event('startup')
async def startup():
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
    dependencies.es = backoff.on_exception(
        wait_gen=backoff.expo,
        max_tries=settings.BACKOFF.RETRIES,
        max_time=settings.BACKOFF.MAX_TIME,
        exception=Exception,
        on_backoff=backoff_hdlr,
        on_success=backoff_hdlr_success,
    )(AsyncElasticsearch)(hosts=[f'{settings.ES.HOST}:{settings.ES.PORT}'])
    dependencies.redis = await backoff.on_exception(
        wait_gen=backoff.expo,
        max_tries=settings.BACKOFF.RETRIES,
        max_time=settings.BACKOFF.MAX_TIME,
        exception=Exception,
        on_backoff=backoff_hdlr,
        on_success=backoff_hdlr_success,
    )(aioredis.create_redis_pool)(
        (settings.REDIS.HOST, settings.REDIS.PORT), minsize=10, maxsize=20
    )


@app.on_event('shutdown')
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await dependencies.es.close()


# Подключаем роутеры к серверу
# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix='/api/v1/film', tags=['Кинопроизведения'])
app.include_router(
    genres.router, prefix='/api/v1/genre', tags=['Жанры'], dependencies=[Depends(decode_jwt)]
)
app.include_router(
    persons.router,
    prefix='/api/v1/person',
    tags=['Персоны'],
    dependencies=[Depends(decode_jwt)],
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8000, log_config=LOGGING, log_level=logging.INFO,
    )
