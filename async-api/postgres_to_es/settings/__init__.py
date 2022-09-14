import os

from postgres_to_es.settings.dev_settings import DevSettings
from postgres_to_es.settings.prod_settings import ProdSettings

settings_param = os.environ.get('SETTINGS', 'prod')

settings_classes = {
    'dev': DevSettings,
    'prod': ProdSettings,
}

if settings_param not in settings_classes:
    expected = ', '.join(settings_classes)
    raise ValueError(
        f'Wrong SETTINGS environment value! Expected {expected}, got {settings_param}.'
    )

settings = settings_classes[settings_param]()
