#!/bin/sh

if [ "$TEST_TESTING" = True ]
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

if [ "$TEST_RUN_WITH_COVERAGE" = True ]
then
    pytest -v -p no:warnings --cov-report=xml --cov-report term-missing:skip-covered --cov=/home/src/app
elif [ "$TEST_RUN_WITH_COVERAGE" = False ]
then
    pytest -v -p no:warnings
fi

exec "$@"