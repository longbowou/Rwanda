# Rwanda
Django based project for a Web freelance services.

## Requirements
- [Docker](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## How to run it?
- Clone the repository
- Build the application
```
$ docker-compose build
```
- Run migrations
```
$ docker-compose run --rm app python manage.py migrate
```
- Run the application
```
$ docker-compose up
```

## Where is the application running?
- Web App - [http://0.0.0.0:8000](http://0.0.0.0:8000/)
- GraphQl - [http://0.0.0.0:8000/graphql/](http://0.0.0.0:8000/graphql/)
- PgAdmin4 - [http://0.0.0.0:5050](http://0.0.0.0:5050)
