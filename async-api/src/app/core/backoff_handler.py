from logging import getLogger

logger = getLogger('backoff')


def backoff_hdlr(details):
    logger.info(
        'Backing off {wait:0.1f} seconds after {tries} tries '
        'calling function {target} with args {args} and kwargs '
        '{kwargs}'.format(**details)
    )


def backoff_hdlr_success(details):
    logger.info(
        'Success done function {target} with args {args} and '
        'kwargs {kwargs} after {tries} tries.'.format(**details)
    )
