# Syriac DASH Scriptchart Backend
Admin UI and API for DASH


## Development
With a working version on Python 3.7+ and Pipenv:

1. Install dependencies
```
$ pipenv install --dev
```

2. Create a database (if not created yet) and migrate. A `DATABASE_URL` can be defined in a `.env` file or set as an environment variable. It will default to `sqlite:///tmp/db.sqlite`
```
$ touch tmp/db.sqlite
$ python manage.py migrate
```

3. Create a superuser
```
$ python manage.py createsuperuser
```

3. (Optional) [Download](https://drive.google.com/a/stanford.edu/uc?export=download&id=1xv5HjkgCr1p5b5qoprNtLgpfmpUWrji-) and load a database dump
```
$ python manage.py loaddata tmp/scripts.json
```

4. Start development server and go to `http://localhost:8000/admin/`
```
$ python manage.py runserver localhost:8000
```

## Testing
- Tests
```
$ python manage.py test
```

- Linting
```
$ flake8
```


## Deployment
Deployment will happen automatically upon a sucessful merge/rebase from develop to master.