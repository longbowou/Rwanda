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
- Seed data
```
$ docker-compose run --rm app python manage.py seed
```
- Run the application
```
$ docker-compose up
```

## Where is the application running?
- GraphQl - [http://localhost:8000/graphql/](http://localhost:8000/graphql/)
- GraphQl Admin - [http://localhost:8000/graphql-admin/](http://localhost:8000/graphql-admin/)
- PgAdmin4 - [http://localhost:5050](http://localhost:5050)
