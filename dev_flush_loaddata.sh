#!/bin/bash
if [ $(which docker-compose) ] ; then
    docker="docker-compose"
else
    docker="docker compose"
fi

$docker exec web python manage.py flush --noinput
$docker exec web python manage.py loaddata data.json