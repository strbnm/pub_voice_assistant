import http
import json
import os
import uuid
from pathlib import Path
from time import sleep

import pytest
from alembic import command
from flask_migrate import Config
from functional.utils import UserTestModel
from pytest_mock import MockerFixture
from sqlalchemy_utils import create_database, drop_database

from app.database import db, session_scope
from app.datastore import user_datastore
from app.main import create_app
from app.models.roles import ProtectedRoleEnum
from app.settings.base import DatabaseSettings
from app.settings.config import settings
from tests.functional.settings import TEST_SRC_DIR_PATH, test_settings


@pytest.fixture(scope='session', autouse=True)
def disable_apm(session_mocker: MockerFixture):
    session_mocker.patch.object(settings.JAEGER, 'ENABLED', False)


@pytest.fixture(scope='session')
def postgres():
    """
    Создает временную БД для запуска тестов и удаляет ее в конце тестовой сессии
    """
    tmp_name = '.'.join([uuid.uuid4().hex, 'pytest'])
    os.environ['DB_PATH'] = tmp_name
    temp_db = DatabaseSettings()
    tmp_url = temp_db.DSN
    create_database(tmp_url)
    try:
        yield tmp_url
    finally:
        drop_database(tmp_url)


@pytest.fixture(scope='session', autouse=True)
def db_init(app):
    """
    Инициализирует тестовую базу данных

    Применяет имеющиеся файлы миграций для создания схемы, таблиц БД
    и их заполнения системными данными (роли пользователей).
    При завершении тестовой сессии откатывает все миграции, очищая БД от артефактов
    """
    with app.app_context():
        config = Config(
            'migrations/alembic.ini'
            if test_settings.RUN_WITH_DOCKER
            else '../migrations/alembic.ini'
        )
        config.set_main_option(
            'script_location',
            'migrations' if test_settings.RUN_WITH_DOCKER else '../migrations',
        )
        command.upgrade(config, 'head')
        yield
        command.downgrade(config, 'base')
        sleep(1)


@pytest.fixture(scope='session')
def app(postgres):
    """Инициализирует Flask с параметрами для тестов"""
    app = create_app()
    app.config.update({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': postgres})
    yield app


@pytest.fixture(autouse=True)
def clear_db(app):
    """Очищает тестовую БД после каждого теста"""
    yield
    with session_scope() as session:
        for table in reversed(db.metadata.sorted_tables):
            session.execute(table.delete())
        base_roles = [
            {
                'id': str(uuid.uuid4()),
                'name': 'guest',
                'description': 'Пользователь онлайн-кинотеатра с базовыми разрешениями.',
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'superuser',
                'description': 'Пользователь с правами администратора (есть все разрешения без их явного назначения).',
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'staff',
                'description': 'Сотрудник кинотеатра, имеющий доступ к службе администрирования.',
            },
        ]
        for role in base_roles:
            user_datastore.create_role(**role)


@pytest.fixture
def client(app):
    """Тестовый клиент для Flask"""
    return app.test_client()


@pytest.fixture(scope='session')
def load_fixture():
    def load(filename):
        with open(Path(TEST_SRC_DIR_PATH) / filename, encoding='utf-8') as file:
            return json.loads(file.read())

    return load


@pytest.fixture(scope='function')
def expected(load_fixture, request):
    return load_fixture(request.param)


@pytest.fixture(name='username')
def temp_user_username():
    return 'test'


@pytest.fixture(name='email')
def temp_user_email():
    return 'test@example.com'


@pytest.fixture(name='password')
def temp_user_password():
    return '#Test1234#'


@pytest.fixture
def account_temp_user(app, username, password, email):
    with app.app_context():
        with session_scope():
            user = user_datastore.create_user(
                username=username, password=password, email=email,
            )
            user_datastore.add_role_to_user(user, ProtectedRoleEnum.guest.value)
            return UserTestModel(**user.__dict__)


@pytest.fixture(name='valid_jwt_pair')
def user_valid_jwt_pair_after_login(client, clear_db, email, password, account_temp_user):
    response = client.post(path='/api/v1/login', data={'login': email, 'password': password},)
    assert response.status_code == http.HTTPStatus.OK
    result = response.json
    assert 'access_token' in result
    assert 'refresh_token' in result
    return result['access_token'], result['refresh_token']


@pytest.fixture(name='invalid_jwt_pair')
def user_invalid_jwt_pair_after_login(client, clear_db, account_temp_user, valid_jwt_pair):
    access_token, refresh_token = valid_jwt_pair
    response = client.post(
        path='/api/v1/logout', headers={'Authorization': f'Bearer {access_token}'}
    )
    assert response.status_code == http.HTTPStatus.OK
    result = response.json
    assert 'message' in result
    assert result['message'] == 'Вы вышли из аккаунта'
    return access_token, refresh_token


@pytest.fixture(name='access_header')
def temp_user_auth_access_header(valid_jwt_pair) -> dict[str, str]:
    access_token, _ = valid_jwt_pair
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture(name='refresh_header')
def temp_user_auth_refresh_header(valid_jwt_pair) -> dict[str, str]:
    _, refresh_token = valid_jwt_pair
    return {'Authorization': f'Bearer {refresh_token}'}
