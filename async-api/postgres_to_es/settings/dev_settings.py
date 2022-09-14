from postgres_to_es.settings.base_settings import CommonSettings


class DevSettings(CommonSettings):
    DEBUG: bool = True
    LOG_LEVEL: str = 'DEBUG'
