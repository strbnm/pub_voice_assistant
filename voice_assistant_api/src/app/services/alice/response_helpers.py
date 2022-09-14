from typing import Optional, Union, Any


def make_button(
    title: str,
    payload: Optional[Union[dict[str, Any], str]] = None,
    url: Optional[str] = None,
    hide: bool = False,
) -> dict[str, Any]:
    """Метод формирования объекта Кнопка.

    :param title: Обязательное свойство для каждой кнопки. Текст кнопки. Максимум 64 символа. Если для кнопки не
        указано свойство url, по нажатию текст кнопки будет отправлен навыку как реплика пользователя.
    :param payload: Произвольный JSON-объект, который Яндекс Диалоги должны отправить обработчику, если данная кнопка
        будет нажата. Максимум 4096 байт.
    :param url: URL, который должна открывать кнопка. Максимум 1024 байта. Если свойство url не указано,
        по нажатию кнопки навыку будет отправлен текст кнопки.
    :param hide: Признак того, что кнопку нужно убрать после следующей реплики пользователя. Допустимые значения:
        false — кнопка должна оставаться активной (значение по умолчанию);
        true — кнопку нужно скрывать после нажатия.
    :return: словарь с параметрами Кнопки
    """

    button = {
        'title': title,
        'hide': hide,
    }
    if payload is not None:
        button['payload'] = payload
    if url is not None:
        button['url'] = url
    return button
