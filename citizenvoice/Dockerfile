FROM python:3.11-alpine3.20

RUN mkdir -p /var/www/dockerize-django/citizenvoice
WORKDIR /var/www/dockerize-django/citizenvoice

COPY ./requirements.txt ./
RUN apk add python3-dev 
RUN apk add --no-cache \
    python3-dev \
    gdal \
    gdal-dev \
    gcc \
    musl-dev \
    geos-dev \
    proj-dev \
    postgresql-dev \
    build-base \
    libjpeg-turbo-dev \
    zlib-dev
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV DJANGO_HOST=0.0.0.0
ENV DJANGO_PORT=8000

CMD [ "python", "manage.py", "runserver"]
