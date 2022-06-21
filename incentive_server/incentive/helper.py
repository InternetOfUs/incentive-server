import requests
import os
import json
from django.http import JsonResponse
from django.utils.timezone import make_aware
import datetime
from .models import UsersCohorts
import logging
logger = logging.getLogger('incentive_server')

from .config.Config import Config
Config = Config()
config_list = Config.get_config()


def insert_user_if_not_exist(user_id, app_id):
    user = list(UsersCohorts.objects.filter(app_id=app_id, user_id=user_id).all().values())
    if len(user) > 0:
        return user[0]['email'], user[0]['cohort']
    last_user = UsersCohorts.objects.all().order_by('-created_at').first()
    cohort = 0
    if None != last_user:
        cohort = not last_user.__dict__['cohort']
    url = config_list['url_wenet_get_user'] % user_id
    response = requests.get(url, headers={"Content-Type": "application/json",
                                     "x-wenet-component-apikey": os.environ.get('COMP_AUTH_KEY')})

    # case the user listed in WeNet profile manager
    try:
        content = json.loads(response.content)
        email = content['email']
        new_user = UsersCohorts.objects.create(user_id=user_id, app_id=app_id, email=email, cohort=cohort)
        logger.info(f'new user {new_user}')
        return email, cohort
    # case the user not  listed in WeNet profile manger (made_up =1 )
    except Exception as e:
        logger.error('problem with profile manager')
        email = 'Bug@bugSite.com'
        new_user = UsersCohorts.objects.create(user_id=user_id, app_id=app_id, email=email, cohort=cohort)
        return email, cohort


def respond_json(message, status_code):
    r = json.loads(json.dumps(
        {'message': message, 'status_code': status_code}))
    return JsonResponse(r, status=r['status_code'])

def api_call(url, call, data=None):
    # call should be either 'post', 'put', 'get or 'delete'
    # data is only for 'post' and 'put' calls
    if call == 'post':
        
        response = requests.post(url,  headers={"Authorization": "Token " + config_list['badgr_token'], "Content-Type": "application/json",
                                                "x-wenet-component-apikey": config_list['api_key']}, data=json.dumps(data))
        return response
    if call == 'put':
        response = requests.put(url,  headers={"Authorization": "Token " + config_list['badgr_token'], "Content-Type": "application/json",
                                                "x-wenet-component-apikey": config_list['api_key']}, data=json.dumps(data))
        return response

    if call == 'get':
        response = requests.get(url,  headers={"Authorization": "Token " + config_list['badgr_token'], "Content-Type": "application/json",
                                                "x-wenet-component-apikey": config_list['api_key']})
        return response
    if call == 'delete':
        if data:
            response = requests.delete(url, headers={"Authorization": "Token " + config_list['badgr_token'], "Content-Type": "application/json",
                                                     "x-wenet-component-apikey": config_list['api_key']}, data=json.dumps(data))
        else:
            response = requests.delete(url,  headers={"Authorization": "Token " + config_list['badgr_token'], "Content-Type": "application/json",
                                                      "x-wenet-component-apikey": config_list['api_key']})
    return response


