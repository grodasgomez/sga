#!/bin/bash
if [ $(which docker-compose) ] ; then
    docker="docker-compose"
else
    docker="docker compose"
fi

$docker build
$docker up -d
$docker exec web python manage.py makemigrations
$docker exec web python manage.py migrate