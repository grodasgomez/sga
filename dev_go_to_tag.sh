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

        $docker build
        $docker up -d
        $docker exec web python manage.py makemigrations
        $docker exec web python manage.py migrate

        echo "Desea recrear la base de datos? (y/n)"
        read bd

        if [ "$bd" == "y" ]; then
            $docker exec web python manage.py flush --noinput
            $docker exec web python manage.py loaddata data.json
        else
            echo "No se recreo la base de datos"
        fi

        echo "Desea correr los tests? (y/n)"
        read bd

        if [ "$bd" == "y" ]; then
            $docker exec web python manage.py test
        else
            echo "No se corrieron los tests"
        fi

        echo "Desea ver la documentacion? (y/n)"
        read bd

        if [ "$bd" == "y" ]; then
            $docker exec web python django_pydoc.py -p 1234 -n 0.0.0.0
        else
            echo "No se vera la documentacion"
        fi

        

        $docker logs -f web

        exit 0
    fi
done

echo "El tag $1 no existe"