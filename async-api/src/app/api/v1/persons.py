from app.api.v1.api_schemas import (
    APIFilmworksList,
    APIPersonDetail,
    APIPersonsList,
    Filter,
    GetFilmsByPersonKWARGS,
    GetPersonByIdKWARGS,
    Pagination,
    Params,
    SearchPersonsKWARGS,
)
from app.core.dependencies import get_film_service, get_person_service
from app.services.controllers.film import FilmService
from app.services.controllers.person import PersonService
from fastapi import APIRouter, Depends, Query

from app.core.config import settings
from app.core.oauth import check_is_subscriber

router = APIRouter()


@router.get('/search', response_model=APIPersonsList, **SearchPersonsKWARGS.get_kwargs())
async def search_persons(
    q: str,
    page: int = Query(settings.ES.DEFAULT_PAGE, gt=0, description='Номер страницы'),
    limit: int = Query(
        settings.ES.DEFAULT_PAGE_SIZE, gt=0, description='Количество объектов на странице'
    ),
    person_service: PersonService = Depends(get_person_service),
) -> APIPersonsList:
    pagination = Pagination(page=page, limit=limit)
    params = Params(query=q, pagination=pagination)
    persons, total = await person_service.get_by_params(params)
    return APIPersonsList(
        total=total, items=persons, page=page, limit=limit, count=len(persons)
    )


@router.get('/{person_id}', response_model=APIPersonDetail, **GetPersonByIdKWARGS.get_kwargs())
async def person_details(
    person_id: str = Query(..., min_length=36, max_length=36, description='UUID объекта'),
    person_service: PersonService = Depends(get_person_service),
) -> APIPersonDetail:
    person = await person_service.get_by_id(person_id)
    return APIPersonDetail(**person.dict())


@router.get(
    '/{uuid}/film/', response_model=APIFilmworksList, **GetFilmsByPersonKWARGS.get_kwargs()
)
async def filmworks_for_person(
    uuid: str = Query(..., min_length=36, max_length=36, description='UUID объекта'),
    page: int = Query(settings.ES.DEFAULT_PAGE, gt=0, description='Номер страницы'),
    limit: int = Query(
        settings.ES.DEFAULT_PAGE_SIZE, gt=0, description='Количество объектов на странице'
    ),
    sort: str = Query(
        '_score',
        regex='-imdb_rating|imdb_rating|_score',
        description='Поле и направление сортировки',
    ),
    film_service: FilmService = Depends(get_film_service),
    is_subscriber: bool = Depends(check_is_subscriber),
) -> APIFilmworksList:
    fil = Filter(person=uuid)
    pagination = Pagination(page=page, limit=limit)
    params = Params(
        pagination=pagination, sort_field=sort, filter_query=fil, is_subscriber=is_subscriber
    )
    films, total = await film_service.get_by_params(params)
    return APIFilmworksList(total=total, items=films, count=len(films), page=page)
