#!/bin/sh

if [ "$SETTINGS" = "prod" ]
then
    echo "Waiting for REDIS..."
    while ! nc -z $REDIS_HOST $REDIS_PORT; do
      sleep 0.1
    done
    echo "REDIS started"
    echo "Waiting for ElasticSearch..."
    while ! nc -z $ES_HOST $ES_PORT; do
      sleep 0.1
    done
    echo "ElasticSearch started"
fi

python app/main.py

exec "$@"