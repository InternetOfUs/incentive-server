# settings_local.py is for all instance specific settings

import random
from settings import *
from mainsite import TOP_DIR
import  os



TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'



##
#
# Database Configuration
#
##




###
#
# CACHE
#
###

# Example 1: LocMemCache (volatile, but simplest)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': '',
        'TIMEOUT': 1,
        'KEY_PREFIX': '',
        'VERSION': 1,
    }
}

# Example 2: A local Memcached instance
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': '127.0.0.1:11211',
#         'KEY_FUNCTION': 'mainsite.utils.filter_cache_key'
#     }
# }



###
#
# Email Configuration
#
###

DEFAULT_FROM_EMAIL = ''  # e.g. "noreply@example.com"

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Example configuration for AWS SES, one possible email backend.
# EMAIL_BACKEND = 'django_ses.SESBackend'

# These are optional -- if they're set as environment variables they won't
# need to be set here as well
# AWS_ACCESS_KEY_ID = ''
# AWS_SECRET_ACCESS_KEY = ''

# Your SES account may only be available for one region. You can specify a region, like so:
# AWS_SES_REGION_NAME = 'us-west-2'
# AWS_SES_REGION_ENDPOINT = 'email.us-west-2.amazonaws.com'
# OR:
# AWS_SES_REGION_NAME = 'us-east-1'
# AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'


###
#
# Static Files Configuration
#
###

# Default localhost configuration is in mainsite/settings.py

# Example: settings for an Azure-based cloud storage backend
# DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
# AZURE_ACCOUNT_NAME = 'azureaccountname'
# AZURE_ACCOUNT_KEY = ''
# MEDIA_URL = 'http://azureaccountname.blob.core.windows.net/'
# AZURE_CONTAINER = 'mediafiles'


###
#
# Celery Asynchronous Task Processing (Optional)
#
###

# BROKER_URL = 'amqp://localhost:5672/'
CELERY_RESULT_BACKEND = None
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULTS_SERIALIZER = 'json'
# CELERY_ACCEPT_CONTENT = ['json']

# Run celery tasks in same thread as webserver (True means that asynchronous processing is OFF)
CELERY_ALWAYS_EAGER = True


###
#
# Application Options Configuration
#
###

HTTP_ORIGIN = "http://127.0.0.1:8000"

# Optionally restrict issuer creation to accounts that have the 'issuer.add_issuer' permission
BADGR_APPROVED_ISSUERS_ONLY = False

# Automatically send an email the first time that recipient identifier (email type) has been used on the system.
GDPR_COMPLIANCE_NOTIFY_ON_FIRST_AWARD = True

# For the browsable API documentation at '/docs'
# For local development environment: When you have a user you'd like to make API requests, 
# as you can force the '/docs' endpoint to use particular credentials.
# Get a token for your user at '/v1/user/auth-token'
# SWAGGER_SETTINGS = {
#     'api_key': ''
# }

LOGS_DIR = TOP_DIR + '/logs'

# debug_toolbar settings
# MIDDLEWARE_CLASSES.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
# INSTALLED_APPS.append('debug_toolbar')
# INTERNAL_IPS = (
#    '127.0.0.1',
# )
# DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}
# DEBUG_TOOLBAR_PATCH_SETTINGS = False

# Key used for symmetrical encryption of pagination cursors.  If not defined, encryption is disabled.  Must be 32 byte,
# base64-encoded random string.  For example:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key())"
#
# PAGINATION_SECRET_KEY = ""

ALLOWED_HOSTS = ['*']

SECRET_KEY = 'QKQ9NKGJLXE8UVS3TXIB0DE7Q9W41J578C5FCRJL'  # ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40))
UNSUBSCRIBE_KEY = '8GGGDKOT4H4O7QU4GPGZ7ERY9GPE2FKALAO81WYP'  # ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40))


###
#
# Logging
#
###

LOGS_DIR = os.path.join(TOP_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': [],
            'class': 'django.utils.log.AdminEmailHandler'
        },

        # badgr events log to disk by default
        'badgr_events': {
            'level': 'INFO',
            'formatter': 'json',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'badgr_events.log')
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },

        # Badgr.Events emits all badge related activity
        'Badgr.Events': {
            'handlers': ['badgr_events'],
            'level': 'INFO',
            'propagate': False,

        }

    },
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(module)s %(message)s'
        },
        'json': {
            '()': 'mainsite.formatters.JsonFormatter',
            'format': '%(asctime)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z',
        }
    },
}

