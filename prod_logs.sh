#!/bin/bash
if [ $(which docker-compose) ] ; then
    docker="docker-compose"
else
    docker="docker compose"
fi

$docker -f docker-compose.prod.yml --env-file=.prod.env logs -f web
