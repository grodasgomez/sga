#!/bin/bash
if [ $(which docker-compose) ] ; then
    docker="docker-compose"
else
    docker="docker compose"
fi
#guarda los tags en una variable
tags=$(git tag -l)
#echo "$tags"
if [ "$#" != "1" ]; then
    echo "Debes proveer un solo tag"
    exit 1
fi
# verifica que el tag exista
for tag in $tags; do
    if [ "$tag" == "$1" ]; then
        #si existe va al tag y lo levanta
        echo "El tag $1 existe"
        git checkout $1

        $docker -f docker-compose.prod.yml --env-file=.prod.env build
        $docker -f docker-compose.prod.yml --env-file=.prod.env up -d
        $docker -f docker-compose.prod.yml --env-file=.prod.env exec web python manage.py makemigrations
        $docker -f docker-compose.prod.yml --env-file=.prod.env exec web python manage.py migrate

        echo "Desea recrear la base de datos? (y/n)"
        read bd

        if [ "$bd" == "y" ]; then
            $docker -f docker-compose.prod.yml --env-file=.prod.env exec web python manage.py flush --noinput
            $docker -f docker-compose.prod.yml --env-file=.prod.env exec web python manage.py loaddata data.json
        else
            echo "No se recreo la base de datos"
        fi

        $docker -f docker-compose.prod.yml --env-file=.prod.env logs -f web

        exit 0
    fi
done


echo "El tag $1 no existe"