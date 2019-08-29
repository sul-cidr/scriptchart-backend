import os

import dj_database_url
from dotenv import load_dotenv


# MySQL Database Drivers
# ======================
#
# MySQLdb is Django's recommended driver for MySQL.  However, it is not
#  always available or installable in shared hosting environments such as
#  Reclaim.  For this reason, it is not included as a dependency of DASH,
#  and we depend on PyMySQL (a pure python driver installable with pip).
#
# There are 2 issues with this approach:
#
# 1) PyMySQL is not officially supported by the Django project, so we must
#  install PyMySQL (0.9.3) to masquerade as mysqlclient (==MySQLdb).  However,
#  that Django >= 2.2 requires a version of MySQLdb >= 1.3.13 -- but PyMySQL
#  installed in this way reports its compatibilty with MySQLdb at only version
#  1.3.12.  This latter is only a shim anyway, so we're re-shimming here to
#  report compatibility with MySQLdb 1.4.2, the current version.  This works
#  just fine (by which I mean all the DB tests from the Django project pass),
#  with the exception of `models.BinaryField`.  So don't use that... :)
#
# 2) There is a bug in Django (#30380) which causes a crash when using PyMySQL
#  in this way with DEBUG=True (this bug has been fixed, but it seems this fix
#  won't be released until Django 3.0, late 2019/early 2020).  As a result, we
#  suggest installing MySQLdb (`pipenv run pip install mysqlclient`) for local
#  development work, and it will be preferred here if available (note that both
#  python and MySQL development headers and libraries will need to be available
#  for pip to be able to compile MySQLdb successfully).  Alternatively, use
#  SQLite for development work.
#
# Background:
#  * https://github.com/PyMySQL/PyMySQL/issues/610
#  * https://github.com/PyMySQL/PyMySQL/issues/790
#  * https://code.djangoproject.com/ticket/30380

try:
    import MySQLdb
except ImportError:
    import pymysql  # pylint: disable=import-error
    pymysql.install_as_MySQLdb()
    pymysql.version_info = (1, 4, 2, 'final', 0)

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.environ.get(
    'SECRET_KEY', '^o)vp)-7km6k&2t5+0ilk4i_jl%#c3a9o^@mojux%2v*8ngdyz')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')
INTERNAL_IPS = ['127.0.0.1']
ADMIN_SITE_HEADER = 'Scriptchart administration'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rangefilter',

    'rest_framework',
    'corsheaders',

    'scriptchart',
    'scripts',
]

if DEBUG:
    INSTALLED_APPS += ['django_extensions', 'debug_toolbar']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE


ROOT_URLCONF = 'scriptchart.urls'

CORS_ORIGIN_ALLOW_ALL = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'scriptchart.wsgi.application'

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'DBNAME': os.path.join(BASE_DIR, 'tmp', 'db.sqlite'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Stop WhiteNoise emitting warnings when running tests
# (see https://github.com/evansd/whitenoise/issues/95)
WHITENOISE_AUTOREFRESH = DEBUG
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.getenv('STATIC_ROOT', 'static')
STATIC_URL = os.getenv('STATIC_URL', '/static/')
IMAGES_ROOT = os.getenv('IMAGES_ROOT', None)

ADMINS = [tuple(_.split(',')) for _ in os.getenv('ADMINS', None).split(';')] \
            if os.getenv('ADMINS', None) else []
SERVER_EMAIL = 'syriacre@blondie.reclaimhosting.com'
EMAIL_SUBJECT_PREFIX = '[DASH] '

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s.%(msecs)03d: %(levelname)s %(message)s',
            'datefmt': '%H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, '..', 'logs', 'django.log'),
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'WARNING',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'console': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
}


if os.environ.get('DEBUG_SQL', False):
    LOGGING = {
        'version': 1,
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            }
        }
    }
