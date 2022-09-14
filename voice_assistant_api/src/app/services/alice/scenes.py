import inspect
import logging
import sys
from typing import Any, Awaitable, Callable, Optional

from app.core.config import settings
from app.models.models import APIFilmsList
from app.services.alice import intents
from app.services.alice.base_scene import Scene
from app.services.alice.fixtures import genres
from app.services.alice.intents import (
    HELP_INTENTS,
    TOP_FILM_INTENTS,
    FILM_INFO_INTENTS,
    PERSON_INFO_INTENTS,
)
from app.services.alice.request import AliceRequest
from app.services.alice.response_helpers import make_button
from app.utils.text import (
    get_plural_form,
    minute_plural,
    film_plural,
    roles_dictionary,
    film_plural_,
    get_string_from_list,
)

logger = logging.getLogger(__name__)


class CommonScene(Scene):
    async def reply(self, request):
        pass

    def handle_global_intents(self, request: AliceRequest):
        intents_set = set(request.intents)
        if intents_set & set(HELP_INTENTS):
            return Helper()
        if intents_set & set(TOP_FILM_INTENTS):
            return TopFilms()
        if intents_set & set(FILM_INFO_INTENTS):
            return FilmInfo()
        if intents_set & set(PERSON_INFO_INTENTS):
            return PersonInfo()

    def handle_local_intents(self, request: AliceRequest) -> Optional[str]:
        raise NotImplementedError()


class Welcome(CommonScene):
    async def reply(self, request: AliceRequest):
        text = (
            'Привет! Я голосовой помощник онлайн-кинотеатра Practix. '
            'Я могу рассказать тебе о фильмах в нашем кинотеатре. '
            'Подсказать фильмы c высоким рейтингом в различных жанрах, '
            'найти фильм по названию или содержанию, рассказать подробности о нем. '
            'А еще могу подсказать фильмы с твоим любимым актером. '
        )
        return await self.make_response(
            text,
            buttons=[
                make_button('Топ комедий', hide=True),
                make_button('Топ триллеров', hide=True),
                make_button('Топ драм', hide=True),
                make_button('Что ты умеешь?', hide=True),
            ],
        )

    def handle_local_intents(self, request: AliceRequest):
        return self.handle_global_intents(request)


class Helper(CommonScene):
    async def reply(self, request):
        text = (
            'Я могу посоветовать интересные фильмы в разных жанрах.\n '
            'Или, например, сказать кто снимался в фильме, и кто его снял.\n'
            'А еще могу подсказать фильмы с твоим любимым актером.'
        )
        return await self.make_response(
            text,
            buttons=[
                make_button('Покажи топ фильмов', hide=True),
                make_button('Подскажи лучшие триллеры', hide=True),
                make_button('Кто автор фильма\n The Star Dreamer?', hide=True),
                make_button('В каких фильмах\n снимался Mark Hamill?', hide=True),
                make_button(
                    'Какой сюжет у фильма\n "Star Wars: Episode V\n - The Empire Strikes Back"?',
                    hide=True,
                ),
            ],
        )

    def handle_local_intents(self, request: AliceRequest):
        pass


class TopFilms(CommonScene):
    def __init__(self):
        self.intents_dict = {
            intents.TOP_BY_GENRE: self.top_by_genre,
            intents.TOP_BY_RATING: self.top_by_rating,
            intents.REPEAT: self.repeat,
            intents.NEXT: self.next,
            intents.PREVIOUS: self.previous,
        }

    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]
        handler = self.intents_handler[intent]
        return await handler(request)

    async def top_by_genre(self, request: AliceRequest):
        genre, genre_id = self.get_genre(request)
        page = self.get_page(request)
        search_response = await request.search_service.get_list_films(
            genre=genre_id, page=page
        )
        if search_response:
            films = self.get_string_film_list(response=search_response, page=page)
            total_item = search_response.total
            plural_form = film_plural[get_plural_form(total_item)]
            per_page = settings.APP.PER_PAGE
            max_page = total_item // per_page + (1 - 0 ** (total_item % per_page))
            if page == 1:
                text = (
                    f'Я нашла {total_item} {plural_form} в жанре {genre}. '
                    f'Вот пять из них с самым высоким рейтингом:\n {films}\n'
                )
            elif 1 < page < max_page:
                text = f'Хорошо. Ещё пять фильмов в жанре {genre}:\n {films}\n'
            else:
                text = f'Хорошо. Последние фильмы в жанре {genre}:\n {films}\n'
            tts, buttons = self.get_tts_and_buttons_with_navigation(
                text=text, page=page, max_page=max_page
            )
            last_intents = request.state.get('last_intents') or request.intents

            return await self.make_response(
                text=text,
                state={'page': page, 'max_page': max_page, 'last_intents': last_intents,},
                buttons=buttons,
                tts=tts,
            )

        return await self.make_response(text='')

    async def top_by_rating(self, request: AliceRequest):
        page = self.get_page(request)
        search_response = await request.search_service.get_list_films(page=page)
        if search_response:
            films = self.get_string_film_list(response=search_response, page=page)
            total_item = search_response.total
            per_page = settings.APP.PER_PAGE
            max_page = total_item // per_page + (1 - 0 ** (total_item % per_page))
            if page == 1:
                text = f'Вот Топ-5 фильмов на основе IMDB рейтинга:\n {films}\n'
            elif 1 < page < max_page:
                text = f'Слушаюсь! Ещё пять фильмов на основе IMDB рейтинга:\n {films}\n'
            else:
                text = f'Ну наконец таки! Последние фильмы в этом длинном списке:\n {films}'
            tts, buttons = self.get_tts_and_buttons_with_navigation(
                text=text, page=page, max_page=max_page
            )
            last_intents = request.state.get('last_intents') or request.intents

            return await self.make_response(
                text=text,
                state={'page': page, 'max_page': max_page, 'last_intents': last_intents,},
                buttons=buttons,
                tts=tts,
            )

        return await self.make_response(text='')

    async def repeat(self, request: AliceRequest):
        state = request.state
        last_phrase = state.get('last_phrase')

        return await self.make_response(text=last_phrase, state=state)

    async def next(self, request: AliceRequest):
        last_intents: dict = request.state.get('last_intents', {})
        if last_intents:
            if intents.TOP_BY_GENRE in last_intents.keys():
                request.request_body['request']['nlu']['intents'].update(last_intents)
                return await self.top_by_genre(request)
            elif intents.TOP_BY_RATING in last_intents.keys():
                request.request_body['request']['nlu']['intents'].update(last_intents)
                return await self.top_by_rating(request)

        return await self.make_response(
            text='Это так не работает! Навигация "Вперед" есть только для списков фильмов.'
        )

    async def previous(self, request: AliceRequest):
        last_intents: dict = request.state.get('last_intents', {})
        if last_intents:
            if intents.TOP_BY_GENRE in last_intents.keys():
                request.request_body['request']['nlu']['intents'].update(last_intents)
                return await self.top_by_genre(request)
            elif intents.TOP_BY_RATING in last_intents.keys():
                request.request_body['request']['nlu']['intents'].update(last_intents)
                return await self.top_by_rating(request)

        return await self.make_response(
            text='Это так не работает! Навигация "Назад" есть только для списков фильмов.'
        )

    @staticmethod
    def get_page(request: AliceRequest):
        prev_page = request.state.get('page', 1)
        max_page = request.state.get('max_page', 1)
        if request.state.get('last_intents'):
            if intents.NEXT in request.intents.keys():
                page = prev_page + 1
            elif intents.PREVIOUS in request.intents.keys():
                page = prev_page - 1
            else:
                page = 1
        else:
            page = 1

        if page > max_page or page < 1:
            return prev_page
        else:
            return page

    @staticmethod
    def get_genre(request: AliceRequest):
        genre = (
            request.intents.get(intents.TOP_BY_GENRE, {})
            .get('slots', {})
            .get('type', {})
            .get('value', '')
        )
        genre = genre.replace('_', '-')
        # Вместо поискового запроса в ES. Словаря genres актуализировать скриптом.
        genre_id = genres.get(genre)['uuid']
        genre_ru = genres.get(genre)['name']
        return genre_ru, genre_id

    @staticmethod
    def get_string_film_list(response: APIFilmsList, page: int) -> str:
        film_list = ((film.title_ru, film.imdb_rating) for film in response.items)
        enumerated_film_list = []
        for idx, (title, rating) in enumerate(film_list, start=(page - 1) * 5 + 1):
            enumerated_film_list.append(f'{idx}. {title}, рейтинг - {rating}')
        films = ' \n'.join(enumerated_film_list)

        return films

    @staticmethod
    def get_tts_and_buttons_with_navigation(
        text: str, page: int, max_page: int
    ) -> tuple[str, list[dict[str, Any]]]:
        if page == 1:
            tts = text.replace('\n', ' sil <[680]> ')
            tts = f'{tts}Чтобы я озвучила следующие пять фильмов скажите "Вперед", "й+Eщё" или "Следующие".'
            buttons = [make_button('Вперед', hide=True)]
        elif 1 < page < max_page:
            tts = text.replace('\n', ' sil <[680]> ')
            tts = (
                f'{tts}Чтобы я озвучила следующие пять фильмов скажите "Вперед", "й+Eщё" или '
                f'"Следующие" sil <[680]> Для озвучивания предыдущих пяти фильмов скажите "Назад" или '
                f'"Предыдущие".'
            )
            buttons = [make_button('Назад', hide=True), make_button('Вперед', hide=True)]
        else:
            tts = text.replace('\n', ' sil <[680]> ')
            tts = f'{tts}Для озвучивания предыдущих пяти фильмов скажите "Назад" или "Предыдущие".'
            buttons = [make_button('Назад', hide=True)]

        return tts, buttons

    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(TOP_FILM_INTENTS):
            return self


class FilmInfo(CommonScene):
    def __init__(self):
        self.intents_dict = {
            intents.FILM_RATING: self.film_rating,
            intents.FILM_GENRES: self.film_genres,
            intents.FILM_ACTORS: self.film_actors,
            intents.FILM_DIRECTOR: self.film_director,
            intents.FILM_WRITERS: self.film_writers,
            intents.FILM_DESCRIPTION: self.film_description,
            intents.FILM_RELEASE_DATE: self.film_release_date,
            intents.FILM_DURATION: self.film_duration,
            intents.DETAILS_FILM: self.film_full_detail,
            intents.REPEAT: self.repeat,
        }

    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]
        handler = self.intents_handler[intent]
        return await handler(request)

    @staticmethod
    async def _get_film_id(request: AliceRequest):
        film_id = request.state.get('film_id', '')
        film_name = request.slots.get('film_name', '')
        if film_name:
            query = film_name
            search_response = await request.search_service.search_films(query_string=query)
            if search_response:
                logger.debug('search response: %s', search_response)
                return search_response.items[0].uuid

        return film_id

    async def film_director(self, request: AliceRequest):
        film_id = await self._get_film_id(request)
        if film_id:
            search_response = await request.search_service.get_film_detail(film_id=film_id)
            if search_response:
                film_title = search_response.title_ru
                directors_list = search_response.directors_names_ru
                if directors_list:
                    directors = get_string_from_list(directors_list)
                    text = f'Фильм "{film_title}" был снят {directors}.'
                else:
                    text = f'У меня нет информации о режиссере, снявшем фильм "{film_title}".'

                return await self.make_response(
                    text=text,
                    state={'film_id': film_id},
                    buttons=[
                        make_button('Актеры фильма', hide=True),
                        make_button('Автор сценария', hide=True),
                        make_button('Рейтинг фильма', hide=True),
                        make_button('Подробнее о фильме', hide=True),
                    ],
                )

        return await self.make_response(text='')

    async def film_writers(self, request: AliceRequest):
        film_id = await self._get_film_id(request)
        if film_id:
            search_response = await request.search_service.get_film_detail(film_id=film_id)
            if search_response:
                film_title = search_response.title_ru
                writers_list = search_response.writers_names_ru
                if writers_list:
                    writers = get_string_from_list(writers_list)
                    text = f'Фильм "{film_title}" был снят по сценарию {writers}'
                else:
                    text = f'У меня нет информации об авторах сценария фильма "{film_title}".'

                return await self.make_response(
                    text=text,
                    state={'film_id': film_id},
                    buttons=[
                        make_button('Актеры фильма', hide=True),
                        make_button('Режиссёр фильма', hide=True),
                        make_button('Рейтинг фильма', hide=True),
                        make_button('Подробнее о фильме', hide=True),
                    ],
                )

        return await self.make_response(text='')

    async def film_actors(self, request: AliceRequest):
        film_id = await self._get_film_id(request)
        if film_id:
            search_response = await request.search_service.get_film_detail(film_id=film_id)
            if search_response:
                film_title = search_response.title_ru
                actors_list = search_response.actors_names_ru
                if actors_list:
                    actors = get_string_from_list(actors_list)
                    text = f'Главные роли в фильме "{film_title}" сыграли:\n {actors}'
                else:
                    text = f'Сожалею, но я не смогла найти имена актеров, сыгравших в фильме "{film_title}".'

                return await self.make_response(
                    text=text,
                    state={'film_id': film_id},
                    buttons=[
                        make_button('Автор сценария', hide=True),
                        make_button('Режиссёр фильма', hide=True),
                        make_button('Рейтинг фильма', hide=True),
                        make_button('Подробнее о фильме', hide=True),
                    ],
                )

        return await self.make_response(text='')

    async def film_description(self, request: AliceRequest):
        film_id = await self._get_film_id(request)
        if film_id:
            search_response = await request.search_service.get_film_detail(film_id=film_id)
            if search_response:
                title = search_response.title_ru
                film_description = search_response.description_ru
                if film_description:
                    text = f'Вот что я нашла по сюжету фильма "{title}":\n {film_description}'
                else:
                    text = f'К сожалению, по фильму "{title}" нет описания сюжета :-('
                return await self.make_response(
                    text=text,
                    state={'film_id': film_id},
                    buttons=[
                        make_button('Актеры фильма', hide=True),
                        make_button('Режиссёр фильма', hide=True),
                        make_button('Рейтинг фильма', hide=True),
                        make_button('Подробнее о фильме', hide=True),
                    ],
                )

        return await self.make_response(text='')

    async def film_duration(self, request: AliceRequest):
        film_id = await self._get_film_id(request)
        if film_id:
            search_response = await request.search_service.get_film_detail(film_id=film_id)
            if search_response:
                title = search_response.title_ru
                duration = search_response.runtime_mins
                if duration:
                    plural_form = minute_plural[get_plural_form(duration)]
                    text = f'Продолжительность фильма "{title}" составляет {duration} {plural_form}.'
                else:
                    text = (
                        f'Я не нашла данных о продолжительности фильма {title} или это сериал.'
                    )

                return await self.make_response(
                    text=text,
                    state={'film_id': film_id},
                    buttons=[
                        make_button('Рейтинг фильма', hide=True),
                        make_button('Подробнее о фильме', hide=True),
                    ],
                )

        return await self.make_response(text='')

    async def film_genres(self, request: AliceRequest):
        film_id = await self._get_film_id(request)
        if film_id:
            search_response = await request.search_service.get_film_detail(film_id=film_id)
            if search_response:
                film_title = search_response.title_ru
                genre_list = [genres[genre.name]['name'] for genre in search_response.genre]
                if len(genre_list) == 1:
                    genre, prefix = genre_list[0], 'в жанре'
                else:
                    genre, prefix = (
                        ' и '.join([', '.join(genre_list[:-1]), *genre_list[-1:]]),
                        'в жанрах',
                    )

                text = f'Фильм "{film_title}" снят {prefix} {genre}.'

                return await self.make_response(
                    text=text,
                    state={'film_id': film_id},
                    buttons=[
                        make_button('Актеры фильма', hide=True),
                        make_button('Режиссёр фильма', hide=True),
                        make_button('Рейтинг фильма', hide=True),
                        make_button('Подробнее о фильме', hide=True),
                    ],
                )

        return await self.make_response(text='')

    async def film_rating(self, request: AliceRequest):
        film_id = await self._get_film_id(request)
        if film_id:
            search_response = await request.search_service.get_film_detail(film_id=film_id)
            if search_response:
                film_rating = search_response.imdb_rating
                film_title = search_response.title_ru
                if film_rating:
                    text = f'Рейтинг фильма "{film_title}" по версии IMDB - {film_rating}.'
                else:
                    text = (
                        f'К сожалению, у меня нет информации о рейтинге фильма "{film_title}".'
                    )

                return await self.make_response(
                    text=text,
                    state={'film_id': film_id},
                    buttons=[
                        make_button('Актеры фильма', hide=True),
                        make_button('Режиссёр фильма', hide=True),
                        make_button('Автор сценария', hide=True),
                        make_button('Подробнее о фильме', hide=True),
                    ],
                )

        return await self.make_response(text='')

    async def film_release_date(self, request: AliceRequest):
        film_id = await self._get_film_id(request)
        if film_id:
            search_response = await request.search_service.get_film_detail(film_id=film_id)
            if search_response:
                title = search_response.title_ru
                film_release_date = search_response.release_date
                film_release_date = film_release_date.strftime('%d.%m.%Y')
                if film_release_date:
                    text = (
                        f'Фильм "{title}" впервые был показан на экранах {film_release_date}.'
                    )
                else:
                    text = f'Я не смогла найти информацию о дате релиза фильма "{title}"'

                return await self.make_response(
                    text=text,
                    state={'film_id': film_id},
                    buttons=[
                        make_button('Актеры фильма', hide=True),
                        make_button('Режиссёр фильма', hide=True),
                        make_button('Автор сценария', hide=True),
                        make_button('Подробнее о фильме', hide=True),
                    ],
                )

        return await self.make_response(text='')

    async def film_full_detail(self, request: AliceRequest):
        film_id = await self._get_film_id(request)
        logger.debug('film_id - %s', film_id)
        if film_id:
            search_response = await request.search_service.get_film_detail(film_id=film_id)
            logger.debug('search_response - %s', search_response)

            if search_response:
                title = search_response.title_ru
                description = search_response.description_ru or 'нет данных'
                actors_list = search_response.actors_names_ru
                actors = get_string_from_list(actors_list) or 'нет данных'
                writers_list = search_response.writers_names_ru
                writers = get_string_from_list(writers_list) or 'нет данных'
                directors_list = search_response.directors_names_ru
                directors = get_string_from_list(directors_list) or 'нет данных'
                rating = search_response.imdb_rating
                genre_list = [genres[genre.name]['name'] for genre in search_response.genre]
                genre = get_string_from_list(genre_list)
                duration = search_response.runtime_mins
                if duration:
                    duration = f'{duration} {minute_plural[get_plural_form(duration)]}'
                release = search_response.release_date or 'нет данных'
                if release:
                    release = release.strftime('%d.%m.%Y')

                text = f"""
                Название: "{title}"
                Жанры: {genre}
                Режиссёр: {directors}
                Сценарий: {writers}
                Актёры: {actors}
                Сюжет фильма: {description}
                IMDB рейтинг фильма: {rating}
                Продолжительность фильма: {duration if duration else 'нет данных'}
                Дата релиза: {release}
                """
                return await self.make_response(text=text, state={'film_id': film_id},)

        return await self.make_response(text='')

    async def repeat(self, request: AliceRequest):
        state = request.state
        last_phrase = state.get('last_phrase')

        return await self.make_response(text=last_phrase, state=state)

    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(FILM_INFO_INTENTS):
            return self


class PersonInfo(CommonScene):
    def __init__(self):
        self.intents_dict = {
            intents.PERSON_ROLES: self.person_roles,
            intents.PERSON_FILMS: self.person_films,
            intents.DETAILS_PERSON: self.person_full_detail,
            intents.REPEAT: self.repeat,
        }

    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]
        logger.debug('intent - %s', intent)
        handler = self.intents_handler[intent]
        return await handler(request)

    @staticmethod
    async def _get_person_id(request: AliceRequest):
        person_id = request.state.get('person_id', '')
        person_name = request.slots.get('person_name', '')
        logger.info('person_id - %s, person_name - %s', person_id, person_name)
        if person_name:
            query = person_name
            logger.info('query person name - %s', query)
            search_response = await request.search_service.search_persons(query_string=query)
            logger.info('search_response for person_id - %s', search_response)
            if search_response:
                return search_response.items[0].uuid
            else:
                return

        return person_id

    async def person_roles(self, request: AliceRequest):
        person_id = await self._get_person_id(request)
        if person_id:
            search_response = await request.search_service.get_person_detail(
                person_id=person_id
            )
            if search_response:
                roles = [roles_dictionary[role] for role in search_response.roles]
                text_roles = get_string_from_list(roles)
                full_name = search_response.full_name_ru
                text = f'{full_name} в своей карьере выступал в роли {text_roles}.'

                return await self.make_response(
                    text=text,
                    state={'person_id': person_id},
                    buttons=[make_button(f'Фильмы {full_name}', hide=True)],
                )

        return await self.make_response(text='')

    async def person_films(self, request: AliceRequest):
        person_id = await self._get_person_id(request)
        logger.info(person_id)
        if person_id:
            search_response_person = await request.search_service.get_person_detail(
                person_id=person_id
            )
            if search_response_person:
                full_name = search_response_person.full_name_ru
                search_response = await request.search_service.get_list_films_by_person(
                    person_id=person_id
                )
                logger.info(search_response)
                if search_response:
                    person_films = [
                        (film.title_ru, film.imdb_rating) for film in search_response.items
                    ]
                    total_count = search_response.total
                    plural_form = film_plural_[get_plural_form(total_count)]
                    if total_count >= 5:
                        phrase = 'Вот 5 самых высоко оцененных: '
                    else:
                        phrase = 'Вот они: '
                    text = [
                        f'{full_name} упоминается в {total_count} {plural_form} нашего кинотеатра. {phrase}'
                    ]
                    for title, rating in person_films:
                        text.append(f'{title}, рейтинг - {rating}')
                    result_text = '\n'.join(text)

                    return await self.make_response(
                        text=result_text, state={'person_id': person_id},
                    )

        return await self.make_response(text='')

    async def person_full_detail(self, request: AliceRequest):
        person_id = await self._get_person_id(request)
        if person_id:
            search_response = await request.search_service.get_person_detail(
                person_id=person_id
            )
            if search_response:
                roles = [roles_dictionary[role] for role in search_response.roles]
                text_roles = get_string_from_list(roles)
                full_name = search_response.full_name_ru.title()
                text = [f'{full_name} в своей карьере выступал в роли {text_roles}.']
                search_film_response = await request.search_service.get_list_films_by_person(
                    person_id=person_id
                )
                if search_film_response:
                    person_films = [
                        (film.title_ru, film.imdb_rating)
                        for film in search_film_response.items
                    ]
                    total_count = search_film_response.total
                    plural_form = film_plural[get_plural_form(total_count)]
                    if total_count >= 5:
                        phrase = 'Вот 5 самых высоко оцененных: '
                    else:
                        phrase = 'Вот они: '
                    text.append(
                        f'В нашем кинотеатре есть {total_count} {plural_form} с его участием. {phrase}'
                    )
                    for title, rating in person_films:
                        text.append(f'{title}, рейтинг - {rating}')
                    result_text = '\n'.join(text)

                    return await self.make_response(
                        text=result_text, state={'person_id': person_id},
                    )

        return await self.make_response(text='')

    async def repeat(self, request: AliceRequest):
        state = request.state
        last_phrase = state.get('last_phrase')

        return await self.make_response(text=last_phrase, state=state)

    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(PERSON_INFO_INTENTS):
            logger.debug('есть локальный интент %s', request.intents)
            return self


def _list_scenes():
    current_module = sys.modules[__name__]
    scenes = []
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, Scene):
            scenes.append(obj)
    return scenes


SCENES = {scene.id(): scene for scene in _list_scenes()}
DEFAULT_SCENE = Welcome
