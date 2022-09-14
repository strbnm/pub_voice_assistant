import logging
import random
from datetime import datetime, timedelta

from db_models import Filmwork
from sqlalchemy_service import session_scope

logger = logging.getLogger(__name__)
logger.setLevel('INFO')
fh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

random.seed(17)


def random_date(start, end):
    """Generate a random datetime between `start` and `end`"""
    return start + timedelta(
        # Get a random amount of seconds between `start` and `end`
        seconds=random.randint(0, int((end - start).total_seconds())),
    )


def main():
    """
    Заполнение таблицы произвольными данными по датам и флагом необходимости наличия подписки.
    Для заполнения в таблицу film_work предварительно необходимо добавить столбец subscription_required вручную
    """
    with session_scope() as sess:
        film_works = sess.query(Filmwork).order_by(Filmwork.id.asc())
        for idx, film_work in enumerate(film_works, start=1):
            start_date = datetime.now() - timedelta(days=365 * 20)
            end_date = datetime.now()
            film_work.creation_date = random_date(start=start_date, end=end_date)
            film_work.subscription_required = (
                False
                if (datetime.now() - film_work.creation_date) >= timedelta(days=365 * 3)
                else True
            )
            logger.info(
                'Record: %s - id: %s, creation_date: %s, subscription_required: %s',
                idx,
                film_work.id,
                film_work.creation_date,
                film_work.subscription_required,
            )
            sess.commit()


if __name__ == '__main__':
    main()
