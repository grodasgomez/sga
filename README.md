# SGA: Sistema de Gestión Agile #
##  Descripción ##
Proyecto de Ingenieria de Software II

## Construcción ##
* ***Lenguaje*** : Python 3.10
* ***Framework*** : Django 4.1

## Requisitos ##
* [Docker Compose](https://docs.docker.com/compose/install/)
* [Docker](https://www.docker.com/)


## Instalación ##
- Clonar el repositorio de [GitHub](link)

- Duplicar el archivo `.env.example`, renombrarlo a `.env` y editar las variables de entorno a conveniencia.

- - Solicitar al equipo las variables de entorno de desarrollo de `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` para la autenticación con Google.

- Estando en el directorio del proyecto, construir la imagen del proyecto :
```
$ docker-compose build
```
## Ejecución ##
Estando en el directorio del proyecto, levantar los containers de la base de datos y del servidor de django en segundo plano:
```
$ docker-compose up -d
```

Para visualizar el log del servidor web:
```
$ docker-compose logs -f web
```
## Migraciones ##
Teniendo la aplicación en ejecución, se aplican las migraciones de cada app instalada en el proyecto:
```
$ docker-compose exec web python manage.py migrate
```
## Detencion ##
```
$ docker-compose stop
```
## Ver documentacion ##
```
$ docker-compose exec web python django_pydoc.py -p 1234 -n 0.0.0.0
```
## Generar HTML
```
$ python django_pydoc.py -w <module>
```
## Realizar pruebas unitarias ##
```
$ docker-compose exec web python manage.py test
```
## Puesta a producción ##
Para levantar el ambiente de producción se utiliza el archivo `docker-compose.prod.yml` que contiene las definiciones de los servicios para el ambiente de producción incluido ngnix y gunicorn

- Duplicar el archivo `.env.example`, renombrarlo a `.prod.env` y editar las variables de entorno a conveniencia.

- Solicitar al equipo las variables de entorno de producción de `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` para la autenticación con Google.

- Estando en el directorio del proyecto, construir las imagenes de producción:
```
$ docker-compose -f docker-compose.prod.yml --env-file=.prod.env build
```
- Levantar la base de datos, el wsgi y el nginx en segundo plano:
```
$ docker-compose -f docker-compose.prod.yml --env-file=.prod.env up -d
```
- Aplicar las migraciones a la base de datos de producción:
```
$ docker-compose -f docker-compose.prod.yml --env-file=.prod.env exec web python manage.py migrate
```
- Visualizar la aplicación abriendo en el navegador `http://localhost`

## Base de datos ##
- Duplicar el archivo `data.json.example`, renombrarlo a `data.json` y editar el archivo a conveniencia.

- Cargar datos en la base de datos
```
$ docker-compose exec web python manage.py loaddata data.json
```
- Limpiar la base de datos
```
$ docker-compose exec web python manage.py flush --noinput
```
