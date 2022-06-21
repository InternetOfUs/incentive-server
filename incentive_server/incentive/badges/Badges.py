import json
from django.http.response import JsonResponse
import requests
import random
import numpy as np
from time import sleep
import os
import logging
from django.db.models import Max
from incentive.Incentive import Incentive
from incentive.models import IssuedIncentives, TaskStatus
from incentive.serializers import TaskStatusSerializer
from incentive.config.Config import Config
from incentive.helper import api_call

Config = Config()
config_list = Config.get_config()
touch_badges = Config.get_touch_badges()
relations_badges = Config.get_relations_badges()
logger = logging.getLogger('incentive_server')


def list_to_dict(l):
    d = {}
    for item in l:
        try:
            key, val = item.split(' ')
            if val == 'None':
                val = 'nolabel!'
            d[key] = val
        except ValueError:  # underline instead of whitespace
            return 'deprecated badgeclass model'
    return d


def update_badgeclass_model(badge):
    l = badge.get('tags')
    d, dd = {}, {}
    for item in l:
        key, val = item.split('_')
        dd[key] = val
    d['taskTypeId'] = 'ask4help' # Sensitive - if changed in the future
    if dd['criteria'] == 'Questions':
        d['label'] = 'nolabel!'
    elif dd['criteria'] == 'Answers':
        d['label'] = 'answerTransaction'
    elif dd['criteria'] == 'AnswersAccepted':
        d['label'] = 'AnswersPickedMessage'
    d['threshold'] = dd['criteriaActions']
    d['app'] = dd['app']
    d['imageUrl'] = badge['image']
    if dd.get('appMessage'):
        d['message'] = dd['appMessage']
    return d


def handle_task_status(request):
    taskTypeId, label, threshold = request['taskTypeId'], request.get('label', 'nolabel!'), request['count']
    logger.info(f'task_status: {request}')
    try:
        threshold = int(threshold)
    except Exception as e:
        return {'message': f'you must provide int after {taskTypeId}'
            , 'status_code': 401}

    app_id = request['app_id']
    user_id = request['user_id']
    user_email = get_user_email(request['user_id'])
    if not user_email:
        return {'message': f'failed to retrieve user email, see logs'
            , 'status_code': 401}
    response = get_all_badges_app(app_id)
    if response['status_code'] != 200:
        logger.error("error getting the badges available from the badgr server")
        return response
    badges = response['badges']  # Ido-Daniel: no need to check whether empty, case covered 4 to 6 lines down

    # Long Answer checker:
    if label == 'answerTransaction':
        taskId = request.get('taskId')
        if taskId:
            url = config_list['get_actions_on_task_app_label'] % (
            app_id, 1, 'answerTransaction', str(user_id)) + f'&taskId={taskId}'  # app, limit, label, user, taskId
        else: # Problem getting taskId - pulling last answerTransaction chronologically
            url = config_list['get_actions_on_task_app_label'] % (
            app_id, 1, 'answerTransaction', str(user_id))
        response = api_call(url, 'get')

        if response.status_code != 200:
            logger.error(f"something's wrong with the task manager: {response.content}")

        else:
            answer = response.json()['transactions'][0]['attributes']['answer']
            if len(answer.split()) >= 40:
                long_answers_count = TaskStatus.objects.filter(user_id=int(user_id), app_id=app_id, taskTypeId=taskTypeId,
                                          label="answerTransactionLong").aggregate(Max('count'))['count__max']
                if not long_answers_count:
                    long_answers_count = 0
                data = {
                    "user_id": str(user_id),
                    "community_id": app_id,  # doesn't matter
                    "app_id": app_id,
                    "taskTypeId": taskTypeId,
                    "label": "answerTransactionLong",
                    "count": long_answers_count + 1
                }
                task_status_serializer = TaskStatusSerializer(data=data)
                if task_status_serializer.is_valid():
                    task_status_serializer.save()
                handle_task_status(json.loads(json.dumps(data)))
                sleep(30)  # delay between potentially being awarded with an answers badge and long answers badge simultaniously


    # Browsing badges to issue:
    badges_to_issue = [b for b in badges if b['taskTypeId'] == taskTypeId
                       and b['label'] == label and int(b['threshold']) <= threshold]
    if len(badges_to_issue) == 0:
        return {'message': 'No badges to issue', 'status_code': 200}

    badge_request = {
        "recipient": {
            "identity": user_email,
            "type": "email",
            "hashed": True
        }
    }

    for i in range(len(badges_to_issue)):
        badge_id = badges_to_issue[i]['id']
        response = issue_badge_if_not_exists(badge_request, badge_id)
        if type(
                response) == requests.models.Response:  # if not Response - User has already got this Badge (returns dict)
            if response.json().get('status').get('success'):
                delivered = 0
                if i == len(badges_to_issue) - 1:
                    delivered = inform_user_badge(badge_id, app_id, user_id)
                badgr = Badges()
                badgr.issue_for_real(delivered, badge_id, user_id, app_id)

    # user_badges = get_all_users_badges(badge_request['recipient']['identity'])

    return response


def get_all_users_badges(user_email):
    response = api_call(config_list['url_badgr'] + config_list['url_all_assertions'] + '?recipient=' + str(user_email),
                        'get')
    # return json.loads(response.result)
    content = json.loads(response.content)
    return content['result']

def get_all_badges():
    response = api_call(config_list['url_badgr'] + config_list['url_get_badges'], 'get')
    
    if response.status_code != 200:
        logger.error(f'something went wrong with badger server: {response.status_code}')
        return {'error': 'something went wrong with badger server', 'status_code': response.status_code}
    content = json.loads(response.content)

    badges_to_response = []
    for r in content.get('result'):
        badge_details = list_to_dict(r.get('tags'))
        if badge_details== 'deprecated badgeclass model':
            badge_details = update_badgeclass_model(r)
        b = get_badge_details_from_response(r)
        badges_to_response.append(b)
    if len(badges_to_response) > 0:
        badges_to_response = sorted(badges_to_response,
                                    key=lambda k: (k['taskTypeId'], k['label'], k['threshold']))
    return {'badges': badges_to_response, 'status_code': 200}


def get_all_badges_app(app_id):
    response = api_call(config_list['url_badgr'] + config_list['url_get_badges'], 'get')

    if response.status_code != 200:
        logger.error(f'something went wrong with badger server: {response.status_code}')
        return {'error': 'something went wrong with badger server', 'status_code': response.status_code}
    content = json.loads(response.content)

    badges_to_response = []
    for r in content.get('result'):
        badge_details = list_to_dict(r.get('tags'))
        if badge_details == 'deprecated badgeclass model':
            badge_details = update_badgeclass_model(r)
        badge_app_id = badge_details.get('app')
        if badge_app_id == app_id:
            b = get_badge_details_from_response(r)
            badges_to_response.append(b)
    if len(badges_to_response) > 0:
        badges_to_response = sorted(badges_to_response,
                                    key=lambda k: (k['taskTypeId'], k['label'], k['threshold']))
    return {'badges': badges_to_response, 'status_code': 200}


def issue_badge_if_not_exists(request, badge_id):
    user_badges = get_all_users_badges(request['recipient']['identity'])
    badge = [b for b in user_badges if b['badgeclass'] == badge_id]
    if len(badge) == 0:
        return api_call(config_list['url_badgr'] + config_list['url_issue_badge'] % badge_id, 'post', request)
    return {"message": "The user already owns this badge", "status_code": 200}


def get_badge_details_from_response(response):
    details = list_to_dict(response.get('tags'))
    if details == 'deprecated badgeclass model':
        details = update_badgeclass_model(response)
        response['criteriaNarrative'] = details.get('message', response.get('description'))

    b = {'id': response.get('entityId'), 'name': response.get('name'), 'description': response.get('description'),
         'message': response.get('criteriaNarrative'), 'taskTypeId': details.get('taskTypeId'),
         'label': details.get('label', 'nolabel!'), 'threshold': int(details.get('threshold')),
         'createdAt': response.get('createdAt'), 'image': details.get('imageUrl'), 'app': details.get('app')}
    return b


def get_user_email(user_id):
    response = api_call(config_list['url_wenet_get_user'] % user_id, 'get')

    if response.status_code != 200:
        logger.error(f"failed to retrieve {user_id}'s email: {response}")
        return
    content = response.json()
    return content.get('email')


def get_user_email_temp(user_id):
    response = api_call(config_list['url_badgr'] + config_list['url_all_assertions'], 'get')

    # return json.loads(response.result)
    content = json.loads(response.content)

    a = []
    # todo: change to get user email from the profile menager
    for result in content['result']:
        a.append(result['recipient']['plaintextIdentity'])
    emails_set = set(a)
    email = random.sample(emails_set, 1)
    return "carlo.caprini@u-hopper.com"


def get_badge_details(badge_id):
    response = api_call(config_list['url_badgr'] + config_list['get_badge_class'] % badge_id, 'get')
    
    content = json.loads(response.content)
    try:
        image = list_to_dict(content['result'][0]['tags']).get('imageUrl')
        description = content['result'][0]['description']
        message = content['result'][0]['criteriaNarrative']
    except AttributeError:  # deprecated badgeclass model
        image = content['result'][0]['image']
        description = content['result'][0]['description']
        tags = content['result'][0]['tags']
        caught_message = False
        for tag in tags:
            if tag[:10] == 'appMessage':
                message = tag[11:]
                caught_message = True
        if not caught_message:
            message = description

    return description, image, message


def inform_user_badge(badge_id, app_id, user_id):
    description, image, message = get_badge_details(badge_id)
    data_wenet = {
        "AppID": str(app_id),
        "UserId": str(user_id),
        "Issuer": "WeNet issuer",
        "IncentiveType": "Badge",
        "Badge": {
            "BadgeClass": badge_id,
            "ImgUrl": image,
            "Criteria": description,
            "Message": message,
        }

    }
    # posting the incentive to wenet platform
    r = api_call(config_list['url_wenet_post_incentive'], 'post', data_wenet)

    # log the issued incentive into dedicate table
    if r.status_code == 202:
        delivered = 1
        logger.info(f'incentive badge {badge_id} issued to the user {user_id}')
    else:
        delivered = 0
        logger.error(f"The user didn't got notification: {r.content}, {badge_id}")
    return delivered


class Badges(Incentive):

    def issue_for_real(self, delivered, badge_id, user_id, app_id):

        try:
            # issue the badge on badgr server

            issued_incentive = {
                "app_id": app_id,
                "user_id": user_id,
                "incentive_id": badge_id,
                "type": 'badge',
                "delivered": delivered
            }

            self.insert_issued_incentive(IssuedIncentives, issued_incentive)

        except Exception as e:
            logger.error(f"error sending the badge to the hub or app for badge {badge_id}")
            print(e)

            return e.__dict__

    def issue(self, user, str_type):
        if str_type == 'touch_events':
            for name, value in touch_badges['badges'].items():
                if np.logical_and(user.touch_events >= value,
                                  self.is_got_incentive(IssuedIncentives, user,
                                                        touch_badges['badges_id'][name]) == False):
                    self.issue_for_real(user, touch_badges['badges_id'][name])
            return True
        else:
            for name, value in relations_badges['badges'].items():
                if np.logical_and(user.relations >= value,
                                  self.is_got_incentive(IssuedIncentives, user,
                                                        relations_badges['badges_id'][name]) == False):
                    self.issue_for_real(user, relations_badges['badges_id'][name])

            return True
