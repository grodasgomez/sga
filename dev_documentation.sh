#!/bin/bash
if [ $(which docker-compose) ] ; then
    docker="docker-compose"
else
    docker="docker compose"
fi

$docker exec web python django_pydoc.py -p 1234 -n 0.0.0.0