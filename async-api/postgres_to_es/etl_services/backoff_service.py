import logging
from functools import wraps
from time import sleep
from typing import Optional


def backoff(
    exception,
    logger: Optional[logging.Logger],
    verbose_name: str = 'backoff',
    start_sleep_time: float = 0.1,
    factor: int = 2,
    border_sleep_time: int = 10,
    max_attempt: int = 100,
):
    """
    Функция для повторного выполнения функции через некоторое время,
    если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param exception: одно исключение или кортеж из исключений, которые должна перехватывать функция декорирования
    :param logger: логгер для логирования процесса выполнения функции
    :param verbose_name: имя декорируемого функцией процесса для отражения в логах
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :param max_attempt: максимальное количество попыток повтора
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            time_out = start_sleep_time
            # Пытаемся выполнить декорируемую функцию в цикле
            # max_attempt - максимальное число попыток выполнения функции при перехвате исключения
            # после чего происходит возврат из функции c трансляцией исключения в вызывающую функцию
            for num_attempt in range(1, max_attempt + 1):
                if logger is not None:
                    logger.info('Attempt number %s for %s...', num_attempt, verbose_name)
                try:
                    connection = func(*args, **kwargs)
                    logger.info(
                        'Attempt number %s for %s is successful.', num_attempt, verbose_name
                    )
                    return connection
                except exception as exc_inner:
                    if logger is not None:
                        logger.exception(
                            'Attempt number %s for %s is unsuccessful!\n'
                            'Error message: %s\nTry %s again after time_out in %s seconds\n',
                            num_attempt,
                            verbose_name,
                            exc_inner,
                            verbose_name,
                            time_out,
                            exc_info=False,
                        )
                    if num_attempt == max_attempt:
                        raise exc_inner
                    sleep(time_out)
                    time_out = (
                        time_out * 2 ** factor
                        if time_out * 2 ** factor < border_sleep_time
                        else border_sleep_time
                    )

        return inner

    return func_wrapper
