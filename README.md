# Syriac DASH Scriptchart Backend
Admin UI and API for DASH


## Development
With a working version on Python 3.7+ and Pipenv:

1. Install dependencies (use `--ignore-pipfile` to use Pipfile.lock instead, and ensure a deterministic enviroment)
```
$ pipenv install --dev --ignore-pipfile
```

2. Create a database (if not created yet) and migrate. A `DATABASE_URL` can be defined in a `.env` file or set as an environment variable. See `.env_tempate` and (here)[https://github.com/kennethreitz/dj-database-url#url-schema] for details. It will default to `sqlite:///tmp/db.sqlite`
```
$ touch tmp/db.sqlite
$ pipenv run python manage.py migrate
```

3. Create a superuser
```
$ pipenv run python manage.py createsuperuser
```

3. (Optional) [Download](https://drive.google.com/a/stanford.edu/uc?export=download&id=1xv5HjkgCr1p5b5qoprNtLgpfmpUWrji-) and load a database dump
```
$ pipenv run python manage.py loaddata tmp/scripts.json
```

4. Start development server and go to `http://localhost:8000/admin/`
```
$ pipenv run python manage.py runserver localhost:8000
```

## Testing
- Tests
```
$ pipenv run python manage.py test
```

- Linting
```
$ pipenv run flake8
```


## Deployment
Deployment will happen automatically upon a sucessful merge/rebase from develop to master.