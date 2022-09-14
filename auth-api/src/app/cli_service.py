from typing import Optional

import click
from flask.cli import with_appcontext
from sqlalchemy.exc import IntegrityError

from app.database import session_scope, db
from app.datastore import user_datastore
from app.models.roles import ProtectedRoleEnum
from app.settings.config import settings


@click.command('createsuperuser')
@click.option('--username', prompt=True, help='Имя пользователя')
@click.option(
    '--email', prompt=True, help='Электронная почта пользователя. Используется как логин'
)
@click.option(
    '--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Пароль'
)
@with_appcontext
def create_superuser(
    username: Optional[str], email: Optional[str], password: Optional[str]
) -> None:
    if not password:
        password = settings.SECURITY.DEFAULT_ADMIN_PASSWORD
    if not username:
        username = settings.SECURITY.DEFAULT_ADMIN_USERNAME
    if not email:
        email = settings.SECURITY.DEFAULT_ADMIN_EMAIL
    try:
        with session_scope():
            user = user_datastore.create_user(
                email=email,
                password=password,
                username=username,
                confirmed=True,
                confirmed_on=db.func.now(),
            )
            user_datastore.add_role_to_user(user, ProtectedRoleEnum.superuser.value)
    except IntegrityError:
        raise ValueError(
            f'Ошибка при создании суперпользователя! Пользователь с e-mail {email} уже существует.',
        )
    print(f'Суперпользователь {email} успешно создан!')
