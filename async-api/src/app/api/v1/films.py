from app.api.v1.api_schemas import (
    APIFilmworkDetail,
    APIFilmworksList,
    Filter,
    GetFilmByIdKWARGS,
    GetFilmsKWARGS,
    Pagination,
    Params,
    SearchFilmsKWARGS,
)
from app.core.dependencies import get_film_service
from app.services.controllers.film import FilmService
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from app.core.config import settings
from app.core.oauth import check_is_subscriber, decode_jwt

router = APIRouter()


@router.get('', response_model=APIFilmworksList, **GetFilmsKWARGS.get_kwargs())
async def get_films(
    sort: str = Query(
        '_score',
        regex='-imdb_rating|imdb_rating|_score',
        description='Поле и направление сортировки',
    ),
    page: int = Query(settings.ES.DEFAULT_PAGE, gt=0, description='Номер страницы'),
    limit: int = Query(
        settings.ES.DEFAULT_PAGE_SIZE, gt=0, description='Количество объектов на странице'
    ),
    genre: str = Query(None, min_length=0, max_length=36, description='UUID жанра'),
    film_service: FilmService = Depends(get_film_service),
    is_subscriber: bool = Depends(check_is_subscriber),
) -> APIFilmworksList:
    pagination = Pagination(page=page, limit=limit)
    fil = Filter(genre=genre)
    params = Params(
        pagination=pagination, sort_field=sort, filter_query=fil, is_subscriber=is_subscriber
    )
    films, total = await film_service.get_by_params(params)
    return APIFilmworksList(total=total, items=films, page=page, limit=limit, count=len(films))


@router.get(
    '/search',
    response_model=APIFilmworksList,
    **SearchFilmsKWARGS.get_kwargs(),
    dependencies=[Depends(decode_jwt)]
)
async def search_films(
    q: str,
    page: int = Query(settings.ES.DEFAULT_PAGE, gt=0, description='Номер страницы'),
    limit: int = Query(
        settings.ES.DEFAULT_PAGE_SIZE, gt=0, description='Количество объектов на странице'
    ),
    film_service: FilmService = Depends(get_film_service),
    is_subscriber: bool = Depends(check_is_subscriber),
) -> APIFilmworksList:
    pagination = Pagination(page=page, limit=limit)
    params = Params(pagination=pagination, query=q, is_subscriber=is_subscriber)
    films, total = await film_service.get_by_params(params)
    return APIFilmworksList(total=total, items=films, page=page, limit=limit, count=len(films))


@router.get(
    '/{film_id}',
    response_model=APIFilmworkDetail,
    **GetFilmByIdKWARGS.get_kwargs(),
    dependencies=[Depends(decode_jwt)]
)
async def film_details(
    film_id: str = Query(..., min_length=36, max_length=36, description='UUID объекта'),
    film_service: FilmService = Depends(get_film_service),
    is_subscriber: bool = Depends(check_is_subscriber),
) -> APIFilmworkDetail:
    if not is_subscriber:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Subscribers only')
    film = await film_service.get_by_id(film_id)
    return APIFilmworkDetail(**film.dict())
