import os
import sys
import dotenv


# the env dir is one level above us
# ENV_DIR = os.path.join(OUR_DIR, '..', 'env')
#
# # activate the virtualenv
# activate_this = os.path.join(ENV_DIR, 'bin', 'activate_this.py')
# execfile(activate_this, dict(__file__=activate_this))


# load up django
from django.core.wsgi import get_wsgi_application

# tell django to find settings entry point'
os.environ['DJANGO_SETTINGS_MODULE'] = 'Lassi.settings'

# hand off to the wsgi application
application = get_wsgi_application()
