# Airport API

API service for airport managing written in DRF

<!-- TOC -->
* [Airport API](#airport-api)
  * [Installing using GitHub](#installing-using-github)
  * [Run using Docker](#run-using-docker)
  * [Getting access](#getting-access)
  * [Features](#features)
  * [Routes](#routes)
    * [airport:](#airport)
    * [user:](#user)
    * [documentation](#documentation)
<!-- TOC -->


## Installing using GitHub

```shell
git clone https://github.com/MasakDirt/airport.git
cd airport
python -m venv venv
pip install -r requirements.txt
set DJANGO_SECRET=<your-secret-key>
set DEBUG=<False>
set PRODUCTION=<False>
set POSTGRES_PASSWORD=<your-postgres-password>
set POSTGRES_USER=<your-postgres-user>
set POSTGRES_DB=<your-postgres-db>
set POSTGRES_HOST=<your-postgres-host>
set POSTGRES_PORT=5432
set PGDATA=<your-postgres-path-for-loading-data>
set DJANGO_SETTINGS_MODULE=airport_core.settings   # include this only for running tests
python manage.py collectstatic
python manage.py migrate
python manage.py loaddata airport_data.json
python manage.py runserver  # http://localhost:8000/
```

## Run using Docker

Docker should be installed. You need to write your `.env` file which must
contain content from `.env.sample`

```shell
docker-compose build
docker-compose up  # http://localhost:8001/
```

## Getting access

1) create user: `api/v1/user/register/`, body:

```json
{
  "email": "your email",
  "password": "your password",
  "first_name": "your first name",  // optional
  "last_name": "your last name"  // optional
}
```

2) login via your credentials: `api/v1/user/register/`, body:

```json
{
  "email": "your email",
  "password": "your password"
}
```

From response you must use `accessToken` in header `Authorization` with
prefix: `Bearer <your-accessToken>`

## Features

- Jwt token Authentication
- Documentation - [routes](#documentation)
- Ordering (`airplanes`, `flights`) and filtering (`routes`, `flights`) with different values and keys
- Search, pagination from DRF
- Managing orders and tickets together
- Managing user
- Admin images uploading and deleting for  airplane
- Signal for auto deleting file from folder
- Throttling: **anonymous user** - 20 requests per day, **user** - 2000 requests per day
- Validation: unique tickets per flight, airplane image size <= 1MB, departure earlier than arrival time in flight
- Custom pagination with showing page and opportunity to change page size


## Routes

### airport:

| route (starts with: `/api/v1/airport/`) | GET |   POST    |    PUT    |  DELETE   |
|:---------------------------------------:|:---:|:---------:|:---------:|:---------:|
|           `airplane_types/ `            |  ✅  | ✅ (admin) |     ❌     |     ❌     |
|         `airplane_types/<id>/`          |  ✅  |     ❌     | ✅ (admin) | ✅ (admin) |
|              `airplanes/`               |  ✅  | ✅ (admin) |     ❌     |     ❌     |
|            `airplanes/<id>/`            |  ✅  |     ❌     | ✅ (admin) | ✅ (admin) |
|     `airplanes/<id>/manage_image/`      |  ❌  | ✅ (admin) |     ❌     | ✅ (admin) |
|               `airports/`               |  ✅  | ✅ (admin) |     ❌     |     ❌     |
|            `airports/<id>/`             |  ✅  |     ❌     | ✅ (admin) | ✅ (admin) |
|                `routes/`                |  ✅  | ✅ (admin) |     ❌     |     ❌     |
|             `routes/<id>/`              |  ✅  |     ❌     | ✅ (admin) | ✅ (admin) |
|                 `crew/`                 |  ✅  | ✅ (admin) |     ❌     |     ❌     |
|              `crew/<id>/`               |  ✅  |     ❌     | ✅ (admin) | ✅ (admin) |
|               `flights/`                |  ✅  | ✅ (admin) |     ❌     |     ❌     |
|             `flights/<id>/`             |  ✅  |     ❌     | ✅ (admin) | ✅ (admin) |
|              `my_orders/`               |  ✅  |     ✅     |     ❌     |     ❌     |
|            `my_orders/<id>/`            |  ✅  |     ❌     |     ❌     |     ❌     |

Create admin:

```shell
python manage.py createsuperuser
```

### user:

| route (starts with: `/api/v1/user/`) | GET | POST | PUT | DELETE |
|:------------------------------------:|:---:|:----:|:---:|:------:|
|             `register/ `             |  ❌  |  ✅   |  ❌  |   ❌    |
|               `login/`               |  ❌  |  ✅   |  ❌  |   ❌    |
|           `token/refresh/`           |  ❌  |  ✅   |  ❌  |   ❌    |
|           `token/verify/`            |  ❌  |  ✅   |  ❌  |   ❌    |
|                `me/`                 |  ✅  |  ❌   |  ✅  |   ✅    |

### documentation

|     File     |        Swagger        |        Redoc        |
|:------------:|:---------------------:|:-------------------:|
| `api/v1/doc` | `api/v1/doc/swagger/` | `api/v1/doc/redoc/` |
