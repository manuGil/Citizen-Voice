# Developer documentation

If you're looking for user documentation, go [here](README.md).


## API Docker container

The api can be reproduced using docker compose as follows:

1. Clone the repository, the latest version is in the `devel` branch.
2. Add a `.env` file to the root of the repository with the following varialbles. Values can be adjusted.

```shell
DATABASE=civo
JDANGO_DB_ENGINE=postgis
DB_USER=citizen
DB_PORT=5432
DJANGO_DEBUG=1  
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
```

3. Create a directory in the root of the repository called `secrets/`, and create the secrets for the Django token and the database password as follows:

```shell
# file name: django_token.txt
<django-token-plain-text>
```

```shell
# file name: django_token.txt
<postgres-superuser-password>
```

4. Build and run using docker compose. The database will be populated with sample data.

```shell
docker compose -f docker-compose.yaml build

docker compose -f docker-compose.yaml up
```

5. Go to the API root: http://localhost:8000/api/v2/

**Open API**
- A schema of the API can be downloaded from: http://localhost:8000/api/v2/schema
- Auto generated documentation is available at: http://localhost:8000/api/v2/schema/redoc

## Development installation

Follow the instruction below to set up a development environment. We use Python 3.10 and Django 4.0.x for development.

### Requirements

* [GDAL 3.3.2](https://gdal.org/download.html) or later
* [PostgreSQL](https://www.postgresql.org/) database with the [PostGIS](https://postgis.net/install/) extension

### Create a virtual environment

Create a virtual environment, activate it, and install the development dependencies in it. This will enable you to run the tests and web-apps later.
[For Windows read here.](https://medium.com/co-learning-lounge/create-virtual-environment-python-windows-2021-d947c3a3ca78)

```shell
# Create a virtual environment, e.g. with
python3 -m venv ./venv

# activate virtual environment
source venv/bin/activate

# make sure to have a recent version of pip and setuptools
python3 -m pip install --upgrade pip setuptools

# (from the project root directory)
# install development dependencies
pip install -r requirements.txt
```

## Running the Django App

1. Create a `.env` file with a secret key for the django project, and the database configuration, such as:
    
    ```shell
    # .env file in ./citizenvoice/
    SECRET_KEY = 'django-insecure-<a hexadecimal string>'
    POSTGRES_USER = '<username>'
    POSTGRES_DBASE = '<database-name>'
    POSTGRES_PWD = '<password>'
    POSTGRES_HOST = '<server-name/IP>'
    POSTGRES_PORT = '<port-number>'
    ```
2. Run the development server from the project directory. Saved changes will be authomatically reloaded:

    ```shell
    python manage.py runserver
    ```

## Running the tests

Running the tests requires an activated virtual environment with the development tools installed.

```shell
# unit tests
cd ./citizenvoice
python manage.py test
```

## Making a release

### Preparation

1. Make sure the `CHANGELOG.md` has been updated
2. Verify that the information in `CITATION.cff` is correct, and that `.zenodo.json` contains equivalent data
3. Make sure that `version` in [setup.cfg](setup.cfg) and  `version` in [CITATION.cff](CITATION.cff) have been bumped to the to-be-released version of the template
4. Run the unit tests with `python manage.py test`
5. Go through the steps outlined above for [generating a new package from the command line](#), and verify that the generated package works as it should.

### GitHub

1. Make sure that the GitHub-Zenodo integration is enabled for https://github.com/NLeSC/python-template
1. Go to https://github.com/NLeSC/python-template/releases and click `Draft a new release`
