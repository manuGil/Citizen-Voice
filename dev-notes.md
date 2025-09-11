



## Pinia Stores

- Getters: allows to filter and manipulate values from the state
- Acctions: allows to update the state of a store.

### Working with a data backend
1. When loading application, create action to retrieve data from backend
2. Use retrieved data to update the store's state
2. When actions update the store's state, they should also update the backend


3. To populate the state with data in the backend 
- Fetch data from the backend
- parse it as JSON
- assign data to store variales.


3. To update data in the backend, 
    - use async functions
    - first, update the state
    - then, update the backend


# creating  api db dump


``` bash
python manage.py dumpdata \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude sessions \
  --exclude auth.user \
  --exclude admin.logentry \
  --indent 2 > civilian-db.json
```


### GitHub

1. Make sure that the GitHub-Zenodo integration is enabled for https://github.com/NLeSC/python-template
1. Go to https://github.com/NLeSC/python-template/releases and click `Draft a new release`

 github

Goto https://github.com/settings/applications/new for creating a new OAuth application on GitHub.
For now:

homepage url : https://127.0.0.1:8000/
callback url : http://localhost/accounts/github/login/callback

# google
Here a webpage how to set up oauth for google: https://plainenglish.io/blog/proper-way-of-using-google-authentication-with-django-and-django-allauth

