#!/bin/sh

echo "Waiting for Django API to be available..."

while ! nc -z django_api 8000; do   
  sleep 2 # Wait for 2 seconds before checking again
done

echo "Django API is up! Starting frontend..."
yarn start
