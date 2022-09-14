from urllib.parse import quote


def encode_uri(url):
    """ Produce safe ASCII urls, like in the Russian Wikipedia"""
    return quote(url, safe="~@#$&()*!+=:;,.?/'")


def get_plural_form(number: int) -> int:
    if number % 10 == 1 and number % 100 != 11:
        return 0
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 > 20):
        return 1
    else:
        return 2


def get_string_from_list(entity_list: list) -> str:
    if entity_list is None:
        return ''
    if len(entity_list) == 1:
        entity_string = entity_list[0]
    else:
        # Формируем принятое в общении завершение последнего перечисления через союз "и".
        # 'Николай, Иван, Петр и Василий' или 'Боевик, Комедия и Драма'
        entity_string = ' и '.join([', '.join(entity_list[:-1]), *entity_list[-1:]])
    return entity_string


film_plural = ['фильм', 'фильма', 'фильмов']
film_plural_ = ['фильме', 'фильмах', 'фильмах']
minute_plural = ['минута', 'минуты', 'минут']

roles_dictionary = {'actor': 'актёра', 'director': 'режиссера', 'writer': 'сценариста'}
