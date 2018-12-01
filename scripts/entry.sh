#!/usr/bin/env bash

_term() {
  echo "Caught SIGTERM signal!"
  kill -TERM "$child" 2>/dev/null
}

trap _term SIGTERM

env

pipenv run python ./manage.py collectstatic --noinput
pipenv run python ./manage.py migrate auth
pipenv run python ./manage.py migrate

pipenv run uwsgi --module games.wsgi:application --check-static=/var/games --env DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} --master  --http :8080 --harakiri 10 --py-autoreload 1 &

child=$!
wait "$child"