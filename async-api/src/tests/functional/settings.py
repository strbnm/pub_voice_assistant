import os

from pydantic import BaseSettings, Field

from app.core.config import settings


class TestingSettings(BaseSettings):
    TESTING: bool = Field(True, description='Для запуска тестов env TESTING должно быть True.')
    RUN_WITH_COVERAGE: bool = Field(
        False, description='Определяет использование pytest-cov при запуске тестов'
    )
    RUN_WITH_DOCKER: bool = Field(
        False, description='Определяет запускаются ли тесты в docker-контейнере'
    )

    class Config:
        env_prefix = 'TEST_'


test_settings = TestingSettings()

TEST_SRC_DIR_PATH = os.path.join(os.path.dirname(__file__), 'testdata')

SERVICE_URL = (
    'http://async-api:8000' if test_settings.RUN_WITH_DOCKER else 'http://127.0.0.1:8000'
)

CACHE_CONFIG = {
    'endpoint': settings.REDIS.HOST,
    'port': settings.REDIS.PORT,
    'ttl': settings.CACHE.TTL,
}
