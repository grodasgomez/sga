#!/bin/bash
if [ $(which docker-compose) ] ; then
    docker="docker-compose"
else
    docker="docker compose"
fi

$docker exec web python manage.py dumpdata > data1.json