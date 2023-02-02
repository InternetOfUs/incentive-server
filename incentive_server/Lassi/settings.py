"""
Django settings for Lassi project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from celery.schedules import crontab
import  Lassi.tasks
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import dirname
import sys
from dotenv import load_dotenv


load_dotenv()

src_dir = (dirname(dirname(__file__)))
sys.path.append(src_dir)

from Config.Config import Config
config = Config.conf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!^1z5le6+bux^$zcvdob95g%5+b48!5r05k==ueh+!*1hd93%p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('INCENTIVE_SERVER_DEBUG')
if DEBUG == 'False':
    DEBUG =False
TEMPLATE_DEBUG = DEBUG
TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(BASE_DIR), "incentive_server/static", "templates"),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.dirname(BASE_DIR), "incentive_server/static", "templates")],
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




# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'incentive',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # 'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

)

REST_FRAMEWORK = {
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',

    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)
}
# cron jobs
# CRONJOBS = [
#     ('00 9,21 * * *', 'incentive.messages.Messages.start'),
#     ('*/1 * * * *', 'incentive.messages.Messages.test_crone')
#
# ]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'timestamp': {
            'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': src_dir + '/Logs/incentive_server.log',
            'formatter': 'timestamp'

        }
    },
    'loggers': {
        'incentive_server': {
            'handlers': ['file'],
            'propagate': True,
        }
    }
}

CORS_ORIGIN_ALLOW_ALL = True

ALLOWED_HOSTS = ['*']

# CORS_URLS_REGEX = r'^dash/pages/streamResponse/'
CORS_URLS_REGEX = r'^dashStream/$'

ROOT_URLCONF = 'Lassi.urls'

WSGI_APPLICATION = 'Lassi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# DATABASES = {
#   'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
# }

# import MySQLdb
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'lassi',
#         'USER': config['user'],
#         'PASSWORD': config['password'],
#         # 'USER': 'root',
#         # 'PASSWORD': '9670',
#         'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
#         'PORT': '3306',
#     }
# }
# import MySQLdb
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lassi',
        # 'USER': 'root',
        # 'PASSWORD': '9670',
        'USER': 'root',
        'PASSWORD': os.getenv('MYSQL_PASSWORD'),
        'HOST': os.getenv('DB'),   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
                    'init_command': 'SET innodb_strict_mode=1',
                    "isolation_level": "READ COMMITTED",
                    # 'ATOMIC_REQUESTS': True
                        # "init_command": "SET storage_engine=INNODB, SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED",

        },
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Template Location
214
if DEBUG:
    MEDIA_URL = '/media/'
    STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "incentive_server/static", "static-only")
    MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "incentive_server/static", "media")
    STATICFILES_DIRS = (
            os.path.join(os.path.dirname(BASE_DIR), "incentive_server/static", "static"),
    )

CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"
CELERY_BEAT_SCHEDULE = {
    "sample_task": {
        "task": "incentive.messages.Messages.test_crone",
        "schedule": crontab(),
    },"second_sample_task": {
        "task": "Lassi.tasks.second_sample_task",
        "schedule": crontab(),
    },
}