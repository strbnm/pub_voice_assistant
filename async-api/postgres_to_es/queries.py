import logging

logger = logging.getLogger(__name__)


def query_all_film_works_id() -> str:
    """Query return all film works (id, updated_at)"""
    query = """
        SELECT id, updated_at
        FROM content.film_work
        ORDER BY updated_at;
    """
    return query


def query_updated_film_works(datetime_value) -> str:
    """Query return updated film works (id, updated_at), after specific datetime"""
    query = f"""
        SELECT id, updated_at
        FROM content.film_work
        WHERE updated_at > '{datetime_value}'
        ORDER BY updated_at;
    """
    return query


def query_updated_genres(datetime_value) -> str:
    """Query return updated genres (id, updated_at), after specific datetime"""
    query = f"""
        SELECT id, updated_at
        FROM content.genre
        WHERE updated_at > '{datetime_value}'
        ORDER BY updated_at;
    """
    return query


def query_last_updated_genre() -> str:
    """Query return last updated genres (id, updated_at)"""
    query = """
        SELECT id, updated_at
        FROM content.genre
        ORDER BY updated_at DESC
        LIMIT 1;
    """
    return query


def query_last_updated_person() -> str:
    """Query return last updated genres (id, updated_at)"""
    query = """
        SELECT id, updated_at
        FROM content.person
        ORDER BY updated_at DESC
        LIMIT 1;
    """
    return query


def query_updated_persons(datetime_value) -> str:
    """Query return updated persons, after specific datetime"""
    query = f"""
        SELECT id, updated_at
        FROM content.person
        WHERE updated_at > '{datetime_value}'
        ORDER BY updated_at;
    """
    return query


def query_film_works_by_genres(genres_id: list) -> str:
    """Query return film_works (id, updated_at) by genres"""
    query = f"""
        SELECT fw.id, fw.updated_at
        FROM content.film_work fw
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        WHERE gfw.genre_id IN {tuple(genres_id)}
        ORDER BY fw.updated_at;
    """
    return query


def query_film_works_by_persons(persons_id: list) -> str:
    """Query return film_works (id, updated_at), where persons were played"""
    query = f"""
        SELECT fw.id, fw.updated_at
        FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
        WHERE pfw.person_id IN {tuple(persons_id)}
        ORDER BY fw.updated_at;
    """
    return query


def query_persons_by_ids(persons_ids: tuple):
    """Query return all persons by specific ids"""
    query = f"""
        SELECT
            content.person.id AS uuid,
            content.person.full_name,
            content.person.full_name_ru,
            array_agg(distinct(cast(content.film_work.id AS text))) AS film_ids,
            array_agg(distinct(content.person_film_work.role)) AS roles
        FROM content.person
        LEFT OUTER JOIN content.person_film_work ON content.person_film_work.person_id = content.person.id
        LEFT OUTER JOIN content.film_work ON content.film_work.id = content.person_film_work.film_work_id
        WHERE content.person.id IN {persons_ids}
        GROUP BY content.person.id;
    """
    return query


def query_genres_by_ids(genres_ids: tuple):
    """Query return all genres by specific ids"""
    query = f"""
        SELECT
            content.genre.id AS uuid,
            content.genre.name,
            content.genre.description
        FROM content.genre
        WHERE content.genre.id IN {genres_ids}
        GROUP BY content.genre.id;
    """
    return query


def query_film_works_by_ids(film_works_id: tuple) -> str:
    """Query return film works by updated film work ids"""
    query = f"""
        SELECT
            content.film_work.id AS uuid,
            content.film_work.rating AS imdb_rating,
            content.film_work.title,
            content.film_work.title_ru,
            content.film_work.description,
            content.film_work.description_ru,
            content.film_work.imdb_titleid,
            content.film_work.runtime_mins,
            content.film_work.imdb_image,
            content.film_work.creation_date AS release_date,
            content.film_work.subscription_required,
            array_agg(distinct(jsonb_build_object('uuid', content.genre.id, 'name', content.genre.name))) AS genre,
            array_agg(distinct(jsonb_build_object('uuid', content.person.id, 'name', content.person.full_name)))
                FILTER (WHERE content.person_film_work.role = 'director') AS directors,
            array_agg(distinct(jsonb_build_object('uuid', content.person.id, 'name', content.person.full_name)))
                FILTER (WHERE content.person_film_work.role = 'actor') AS actors,
            array_agg(distinct(jsonb_build_object('uuid', content.person.id, 'name', content.person.full_name)))
                FILTER (WHERE content.person_film_work.role = 'writer') AS writers,
            array_agg(distinct(content.person.full_name)) FILTER (WHERE content.person_film_work.role = 'director')
                AS directors_names,
            array_agg(distinct(content.person.full_name)) FILTER (WHERE content.person_film_work.role = 'actor')
                AS actors_names,
            array_agg(distinct(content.person.full_name)) FILTER (WHERE content.person_film_work.role = 'writer')
                AS writers_names,
            array_agg(distinct(content.person.full_name_ru)) FILTER (WHERE content.person_film_work.role = 'director')
                AS directors_names_ru,
            array_agg(distinct(content.person.full_name_ru)) FILTER (WHERE content.person_film_work.role = 'actor')
                AS actors_names_ru,
            array_agg(distinct(content.person.full_name_ru)) FILTER (WHERE content.person_film_work.role = 'writer')
                AS writers_names_ru
        FROM content.film_work
        LEFT OUTER JOIN content.genre_film_work ON content.genre_film_work.film_work_id = content.film_work.id
        LEFT OUTER JOIN content.person_film_work ON content.person_film_work.film_work_id = content.film_work.id
        LEFT OUTER JOIN content.genre ON content.genre.id = content.genre_film_work.genre_id
        LEFT OUTER JOIN content.person ON content.person.id = content.person_film_work.person_id
        WHERE content.film_work.id IN {film_works_id}
        GROUP BY content.film_work.id;
    """
    return query
