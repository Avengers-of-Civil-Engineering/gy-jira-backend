import sys
from pathlib import Path
from .read_env import read_env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = read_env()

SECRET_KEY = env('SECRET_KEY')

DEBUG = env('DEBUG')
LOG_DB_SQL = env('LOG_DB_SQL')
ADMIN_URL_SUFFIX = env('ADMIN_URL_SUFFIX')

ALLOWED_HOSTS = ['*', ]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',

    'jira',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jira_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jira_backend.wsgi.application'

DATABASES = {
    'default': env.db("DATABASE_URL")
}

if not DEBUG:
    DATABASES['default']['CONN_MAX_AGE'] = 60

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_NAME = "gy_jira_sessionid"

AUTH_USER_MODEL = "jira.User"

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '240/minute',
        'user': '400/minute'
    },
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
    'JSON_UNDERSCOREIZE': {
        'no_underscore_before_number': True,
    },
}

log_dir = BASE_DIR / "logs"
if not log_dir.exists():
    log_dir.mkdir()


def skip_static_requests(record):
    if isinstance(record.args[0], str) and record.args[0].startswith('GET /static/'):
        return False
    return True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        # use Django's built in CallbackFilter to point to your filter
        'skip_static_requests': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_static_requests
        }
    },
    'formatters': {
        'standard': {
            'format': '[%(levelname)s][%(asctime)s][%(name)s][%(filename)s:%(lineno)d]%(message)s',
            'style': '%',
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': sys.stderr
        },
        'file': {
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': log_dir / "app.log"
        },
        'db': {
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': log_dir / "db.log"
        },
        'django.server': {
            'level': 'INFO',
            'filters': ['skip_static_requests'],
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    'loggers': {
        'jira': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'DEBUG' if LOG_DB_SQL else 'INFO',
            'handlers': ['db'],
            'propagate': False,
        },
        'root': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}

if not DEBUG:
    LOGGING['loggers'] = {
        'root': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        }
    }

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
