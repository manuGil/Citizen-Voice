# Quick Start

This guide provides a quick start for developers to set up the Citizen Voice application on their local machines. It covers the essential steps to get the application running, and start developing.

## Prerequisites

### For Django APIs

- **Python**: Ensure you have Python 3.10 or higher installed on your machine. You can download it from [Python's official website](https://www.python.org/downloads/). **Required if developing the APIs.**
- **PostgreSQL**: Ensure you have PostgreSQL 16.0 or higher installed and running with the [PostGIS extension](https://postgis.net/documentation/getting_started/#installing-postgis). You can download it from [PostgreSQL's official website](https://www.postgresql.org/download/). **Required if developing the APIs.**
- **GDAL**: Install a version of [GDAL](https://gdal.org/en/stable/) compatible with your version of [GeoDJango](https://docs.djangoproject.com/en/5.2/ref/contrib/gis/). Installing GDAL can be combersome in some operatint systems. In such cases, using a conda environment might be the quickest way to start.

### For Citizen Mappping and Community Dashboard

- **Node.js**: Ensure you have Node.js (version 22 or higher) installed. You can download it from [Node.js official website](https://nodejs.org/).
- **Yarn**: We prefer [yarn](https://classic.yarnpkg.com/lang/en/docs/install/#mac-stable) but you can use another dependencies manager compatible with NuxtJS 3.

### For Services Deployment and Configuration

- **Docker**: Ensure you have Docker and Docker Compose installed on your machine (v2.22.0 or later). You can download it from [Docker's official website](https://www.docker.com/get-started). 


## Setting Up the Development Environment

1. Clone the repository, the latest version is in the `devel` branch.

### Django APIs

2. Add an `.env` file to the root of the repository with the following variables.

```shell
POSTGRES_USER=citizen
POSTGRES_DBASE=civo
POSTGRES_PWD=admin@voice
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DJANGO_DB_ENGINE=postgis
DJANGO_ALLOWED_HOSTS= localhost 127.0.0.1 [::1] api cvportal
DJANGO_DEBUG=1 # 0 for production
```

3. Create a directory in the root of the repository called `secrets/`, and create the secrets for the Django token and the database password as follows:

```shell
# file name: django_token.txt
<django-token-plain-text>
```

```shell
# file name: postgres_password.txt
# Make sure this matches the one used in POSTGRES_PWD
<postgres-superuser-password>
```

4. Create a new superuser on your PostgreSQL with a *name* and *password* that matches the ones used in the `.env` file and the `postgres_password.txt` secret.
5. Create a PostgreSQL database in your server with a name that matches `POSTGRES_DBASE` above, and make the new user an owner of the database, and allow all previlages for this user to the database.


6. Install the Django depencies in `citizenvoice/requirements.txt`

```shell
pip install -r citizenvoice/requirements.txt
```

7. Make and apply the migrations. Do the following:

```shell
cd citizenvoice/
python manage.py makemigrations
python manage.py migrate

# If you get an error, 
## check your database configuration, .env, and settings.py 
# If you see this: No settings is available for selected database engine!
## Make sure the lines 34 and 36 in settings.py ARE NOT commented. ## And that the names in your .env file matches the ones used by your database.
```

8. Start the Django development server.

```shell
python manage.py runserver

# server will start on http://127.0.0.1:8000/
```

The APIs will be available as follows:

- Voice: **http://localhost:8000/voice/v3**
- Civilian: **http://localhost:8000/civilian/v1**
- Django Admin:  **http://localhost:8000/api/admin**

```{important}
Notice that when running the Apps idependently, the TCP port is part of the URLs
```

9. Create a superuser for the Django Admin App

```shell
python manage.py createsuperuser

# enter a username and password. 
# Use this credentials to login to the Django Admin
```

### Citizen Mapping

This is a `NuxtJS 3` app.

1. Install the dependencies.

```shell
cd maptool/
yarn install
```

2. Rund the App.

```shell
yarn run dev

# Press CTRL + C to stop the app
```

### Community Dashboard

This is a `NuxtJS 3` app.

1. Install the dependencies.

```shell
cd cv-portal/
yarn install
```

2. Rund the App.

```shell
yarn run dev

# Press CTRL + C to stop the app
```

````{important}
At this point, the Apps contained in the repository can be developed and test. However, the database remains empty (except for user information). 
The `/citizenvoice/civilian-db.json` contains sample data (surveys and answers) that can be loaded in an empty database using the Django command:

```shell
python manage.py loaddata civilian-db.json
```
````

### Services Deployment

We use Docker to create and manage containers for integrating the Apps and services.

There are `docker files` for the following Apps:

- Django APIs
- Citizen Mapping
- Community Dashboard

We use Docker compose to integrate the services and `NginX` as reverse proxy.

```{warning}
When building the containers, **lines 34 and 36 in `settings.py` must be commented out.** Otherwise the environment variables loaded by Django and Docker compose might conflict and some services won't work as expected.
```

1. Build the containers

```shell
# from CitizenVoice/
docker compose build
```

2. Run the containers
   
```shell
docker compose --env-file .env up
```

The following services will be available:

- Voice API: **http://localhost/voice/v3**
- Civilian  API: **http://localhost/civilian/v1**
- Django Admin:  **http://localhost/api/admin**
- Mapping Citizen App: **http://localhost/citizen-map**
- Community Dashboard: **http://localhost/api/cv-portal**

```{important}
Notice that when using Docker, the TCP port is not part of the URLs
```
