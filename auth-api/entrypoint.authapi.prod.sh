#!/bin/sh

if [ "$SETTINGS" = "prod" ]
then
    echo "Waiting for REDIS..."
    while ! nc -z $REDIS_HOST $REDIS_PORT; do
      sleep 0.1
    done
    echo "REDIS started"
    echo "Waiting for Postgresql..."
    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done
    echo "Postgresql started"
fi

python app/wsgi.py

exec "$@"