## Запуск сервиса auth-api

_Все команды в терминале выполняются в каталоге /auth-api._

1. Переименовать файл .env.sample в .env для dev (переменная SETTINGS=dev) и .env.prod для production (переменная SETTINGS=prod). 
Изменить при необходимости значения переменных окружения (не обязательно) 
2. Поднять проект в docker-compose
```shell
docker-compose up --build -d  # для разработки
или
docker-compose -f docker-compose.prod.yaml up --build -d  # для производтва
```
2. Обновить состояние базы данных до последней миграции. 
```shell
docker exec -it auth_api flask db upgrade
```
3. Создать суперпользователя
```shell
docker exec -it auth_api flask createsuperuser
```
4. Документация openapi сервера для dev доступна по адресу:
```http request
http://127.0.0.1:8088
```

## Авторизация с помощью OAuth2
Для авторизации предпочтительно использовать Firefox (удобнее работать с ответами в формате JSON).

URL сервисов авторизации (ввести в адресной строке браузера):
```http request
http://127.0.0.1/api/v1/login/google  # для Google
```
или
```http request
http://127.0.0.1/api/v1/login/yandex  # для Yandex
```
Скопировать полученный access-токен и использовать для запросов к остальным endpoints сервиса.

## Запуск тестов
Для запуска тестов выполнить:
```shell
docker-compose -f docker-compose.test.yaml up --build
```

## Схема API

Схема API сервиса представлена в файле [docs/openapi_auth_api.yaml](docs/openapi_auth_api.yaml)
