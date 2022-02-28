# -*- coding: utf-8 -*-
import django

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Lassi.settings")
django.setup()

import time
from datetime import  datetime
import logging


logger = logging.getLogger('incentive_server')


from  incentive.messages.Messages import test_crone





if __name__ == '__main__':

    while True:
        if datetime.strptime('9:00', '%H:%M').time() <= datetime.now().time() < datetime.strptime('10:00', '%H:%M').time() \
                or datetime.strptime('21:00', '%H:%M').time() <= datetime.now().time() < datetime.strptime('22:00','%H:%M').time():
            print('started1')
            test_crone()
            print('finished')
            time.sleep(3600)

