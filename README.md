# SGA: Sistema de Gestión Agile #
##  Descripción ##
Proyecto de 

## Construcción ##
* ***Lenguaje*** : Python 3.10
* ***Framework*** : Django 4.1

## Requisitos ##
* [Docker Compose](https://docs.docker.com/compose/install/) 
* [Docker](https://www.docker.com/)


## Instalación ##
- Clonar el repositorio de [GitHub](link)
- Renombrar el archivo `.env.example` a `.env` y editar las variables de entorno a conveniencia.
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