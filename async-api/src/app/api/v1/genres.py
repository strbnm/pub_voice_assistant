from app.api.v1.api_schemas import (
    APIGenreDetail,
    APIGenresList,
    GetGenreByIdKWARGS,
    GetGenresKWARGS,
    Pagination,
    Params,
)
from app.core.dependencies import get_genre_service
from app.services.controllers.genre import GenreService
from fastapi import APIRouter, Depends, Query

from app.core.config import settings

router = APIRouter()


@router.get('', response_model=APIGenresList, **GetGenresKWARGS.get_kwargs())
async def get_genres(
    page: int = Query(settings.ES.DEFAULT_PAGE, gt=0, description='Номер страницы'),
    limit: int = Query(
        settings.ES.DEFAULT_PAGE_SIZE, gt=0, description='Количество объектов на странице'
    ),
    genre_service: GenreService = Depends(get_genre_service),
) -> APIGenresList:
    pagination = Pagination(page=page, limit=limit)
    params = Params(query='', pagination=pagination)
    genres, total = await genre_service.get_by_params(params)
    return APIGenresList(total=total, items=genres, count=len(genres), page=page)


@router.get('/{genre_id}', response_model=APIGenreDetail, **GetGenreByIdKWARGS.get_kwargs())
async def genre_details(
    genre_id: str = Query(..., min_length=36, max_length=36, description='UUID объекта'),
    genre_service: GenreService = Depends(get_genre_service),
) -> APIGenreDetail:
    genre = await genre_service.get_by_id(genre_id)
    return APIGenreDetail(**genre.dict())
