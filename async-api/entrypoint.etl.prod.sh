#!/bin/sh

if [ "$SETTINGS" = "prod" ]
then
    echo "Waiting for Postgresql..."
    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done
    echo "Postgresql started"

    echo "Waiting for ElasticSearch..."
    while ! nc -z $ES_HOST $ES_PORT; do
      sleep 0.1
    done
    echo "ElasticSearch started"
fi

python postgres_to_es/main.py

exec "$@"