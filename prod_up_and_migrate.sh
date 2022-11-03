#!/bin/bash
if [ $(which docker-compose) ] ; then
    docker="docker-compose"
else
    docker="docker compose"
fi

$docker -f docker-compose.prod.yml --env-file=.prod.env build
$docker -f docker-compose.prod.yml --env-file=.prod.env up -d
$docker -f docker-compose.prod.yml --env-file=.prod.env exec web python manage.py makemigrations
$docker -f docker-compose.prod.yml --env-file=.prod.env exec web python manage.py migrate