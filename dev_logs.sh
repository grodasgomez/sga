#!/bin/bash
if [ $(which docker-compose) ] ; then
    docker="docker-compose"
else
    docker="docker compose"
fi

$docker logs -f web