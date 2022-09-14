## Подготовка к запуску сервиса async-api

_Все команды в терминале выполняются в каталоге /async-api._

1. Переименовать файл .env.sample в .env для dev (переменная SETTINGS=dev) и .env.prod для production (переменная SETTINGS=prod). 
Изменить при необходимости значения переменных окружения в части доступа к Postgresql и др. 
2. Скопировать базу данных из admin-panel (при остановленном postgres) в папку async-api/data
3. Запустить postgres командой `docker-compose up db-async`
4. Запустить скрипт `async-api/postgres_to_es/fill_db_subscription_required/main.py` для заполнения базы данных фейковыми данными по дате создания фильма и флагом subscription_required.
5. Остановить postgres - Ctrl+C

### Запуск сервиса в Docker-compose
Для сборки, запуска и остановки всех контейнеров в production используются команды:

```shell
# сборка и запуск
docker-compose -f docker-compose.prod.yaml up --build

# или в режиме daemon:
docker-compose -f docker-compose.prod.yaml up --build -d

# для остановки контейнеров с очисткой volumes:
docker-compose -f docker-compose.prod.yaml down -v
```

Для сборки и запуска контейнеров для тестов используются команды:

```shell
# для сборки и запуска всех контейнеров с тестами
docker-compose -f docker-compose.test.yaml up --build

# для запуска контейнеров с ES, REDIS и APP и запуском тестов из IDE
docker-compose -f docker-compose.test.yaml up elasticsearch redis app-api

# для запуска контейнеров с ES и REDIS и запуска тестов из IDE c помощью тестового сервера приложений
docker-compose -f docker-compose.test.yaml up elasticsearch redis 
```
### Особенности запуска тестов
При необходимости оценки охвата кода тестами c помощью pytest-cov перед запуском контейнеров с тестами необходимо 
установить значение переменной окружения `TEST_RUN_WITH_COVERAGE=True`. По умолчанию установлено значение False.
В этом случае запуск тестов будет вестись с использованием тестового сервера приложения, запускаемого на 
период тестовой сессии в контейнере testing.
### Состав контейнеров docker-compose

- **db (postgres)** - база данных Postgresql. Не используется в test. *(Для корректной работы нужно скопировать файлы БД в папку data в корневом каталоге репозитория)*
- **elasticsearch (elasticsearch)** - сервер ElasticSearch.
- **kibana (kibana)** - сервер Kibana (для визуальной отладки ES в браузере). Не используется в production и test
- **nginx (nginx)** - web-сервер и обратный прокси-сервер. Не используется в test.
- **app-api (fastapi)** - сервис Async API.
- **etl (etl-service)** - сервис ETL (Postgresql to ElasticSearch). Не используется в test.
- **redis (api-redis)** - база данных Redis для сервиса Async API.
- **testing (testing)** - функциональные тесты. Не используется в dev и production.
