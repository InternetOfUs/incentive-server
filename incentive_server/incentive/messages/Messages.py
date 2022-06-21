import requests
import pandas as pd
import json
from datetime import datetime, timezone
from django.http import JsonResponse
from django.db.models import Max
import random
from incentive.Incentive import Incentive
from incentive.models import IssuedIncentives, IncentiveMessages, WeNetApps, \
    Complaint, TaskStatus
from incentive.config.Config import Config
from incentive.badges.Badges import get_all_badges_app
from incentive.helper import insert_user_if_not_exist, api_call, respond_json
import logging
import os

Config = Config()
config_list = Config.get_config()
logger = logging.getLogger('incentive_server')


# def get_user_actions_json(app, limit, query_label, user):
#    url = config_list['get_actions_on_task_app_label'] % (
#        app, 1000, query_label, str(user))
#    actions = requests.get(url, headers={"x-wenet-component-apikey": os.environ.get('COMP_AUTH_KEY')})
#    if actions.status_code != 200:
#        logger.error(f"something's wrong with the task manager: {actions.content}")
#        pass    # ???
#    actions_json = actions.json()
#    return actions_json

# def get_user_number_actions_left_for_badge(user, query_label, message_type, app):
#    actions_json = get_user_actions_json(app, 1000, query_label, user)
#    # to get the right badge threshold
#    if message_type =='Badge_Questions':
#        badge_type = 'Questions'
#    else:
#        badge_type = 'Answers'
#
#    if not actions_json['transactions']:
#        n_user_actions = 0
#    else:
#        n_user_actions = len(actions_json['transactions'])
#    response = get_all_badges_app(app)
#    if response['status_code'] != 200:
#        logger.error("error getting the badges available from the badgr server")
#        return
#    badges = response['badges']
#    badges = [b for b in badges if b['tags'][0] == badge_type]
#    n_actions_to_badge = []
#    for badge in badges:
#        n_actions_to_badge.append(int(badge['tags'][1]) - n_user_actions)
#    n_actions_to_badge = [n for n in n_actions_to_badge if n > 0]
#    if len(n_actions_to_badge)==0:
#        # if user has already got all badges
#        return
#    return min(n_actions_to_badge)

# def user_inactivity_days(app, user, query_label):
#     actions_json = get_user_actions_json(app, 1000, query_label, user)
#     now = datetime.now()
#     if actions_json['transactions']:
#         ts_list = [ t['_lastUpdateTs'] for t in actions_json['transactions']]
#         diff = now - datetime.utcfromtimestamp(max(ts_list))
#         return diff.days
#     return get_user_joining_date(user)

# def is_question_related_to_user(user, question_transactions):
#    question_metadata = question_transactions[0]['messages']
#    users = []
#    for d in question_metadata:
#        if d['label'] == 'QuestionToAnswerMessage':
#            users.append(d['receiverId'])
#    return str(user) in users
#
#
# def open_question_for_user(user, question_transactions):
#    # check if the question open to the user
#    if not is_question_related_to_user(user, question_transactions):
#        return False
#
#    for t in question_transactions:
#    # check whether the user is the owner
#        if t['label'] == 'CREATE_TASK' and t['actioneerId'] == str(user):
#            return False
#    # check whether the user has already answered
#        if t['label'] == 'answerTransaction' and t['actioneerId'] == str(user):
#            return False
#    return True
#
#
# def there_are_open_questions_user(user, app):
#    r = requests.get( config_list['url_wenet_get_app_open_tasks'] % app,
#        headers={"x-wenet-component-api key": os.environ.get('COMP_AUTH_KEY')})
#    if r.status_code != 200:
#        logger.error(f'error getting open tasks {r.content}')
#        pass
#    r_json = r.json()
#    user_answer = []
#    if r_json['total'] == 0:
#        return False
#    for i in range(len(r_json['tasks'])):
#        user_answer.append(open_question_for_user(user, r_json['tasks'][i]['transactions']))
#    return True in user_answer

# def send_incentive_message(user, app, incentive, query_label, message_type, user_messages, frequency, repeat, inactivity):
#    days_inactivity = user_inactivity_days(app,user, query_label)
#    user_actions = get_user_actions_json(app, 1000, query_label, user)
#    if len(user_messages) > 0:
#        #check the last time the user issued the incentive
#            days_last_message = last_issued_message_days(user_messages)
#    else:
#        #getting the user inactivity from joining_date
#
#        days_last_message = get_user_joining_date(user)
#    if days_inactivity >= inactivity and days_last_message >= random.randint(1, 4) and len(user_messages) <= repeat:
#        if message_type == "OpenQuestions":
#            if not there_are_open_questions_user(user, app):
#                return
#        # elif message_type == "QuestionsRecently":     (no derived conditions)
#        elif message_type == "QuestionsYet":
#            if user_actions:
#                return
#        elif message_type == "Badge_Answers" or message_type == 'Badge_Questions':
#            n_actions = get_user_number_actions_left_for_badge(int(user), query_label, message_type, app)
#            # case was error or user got all badges
#            if n_actions:
#                message_to_issue = Messages()
#                return message_to_issue.issue_for_real(incentive, user, app, extra=n_actions)
#        message_to_issue = Messages()
#        return message_to_issue.issue_for_real(incentive, user, app)

def get_user_joining_date(user):
    # todo: check the date the user joined to the app.
    profile = api_call(config_list['url_wenet_get_user'] % str(user), 'get')

    if profile.status_code != 200:
        logger.error(f'Something wrong with the service api for user {user}: {profile.content}')
        return 0
    profile_json = profile.json()
    joining_date = datetime.utcfromtimestamp(profile_json['_creationTs'])
    now = datetime.now()
    diff = now - joining_date
    return diff.days


def get_user_number_actions_left_for_badge(user, taskTypeId, label, app):
    task_count = \
    TaskStatus.objects.filter(user_id=user, app_id=app, taskTypeId=taskTypeId, label=label).aggregate(Max('count'))[
        'count__max']
    if not task_count:
        task_count = 0

    response = get_all_badges_app(app)
    if response['status_code'] != 200:
        logger.error("error getting the badges available from the badgr server")
        return
    badges = response['badges']
    badges = [b for b in badges if b['taskTypeId'] == taskTypeId and b['label'] == label]
    n_actions_to_badge = []
    for badge in badges:
        n_actions_to_badge.append(int(badge['threshold']) - task_count)
    n_actions_to_badge = [n for n in n_actions_to_badge if n > 0]
    if len(n_actions_to_badge) == 0:
        # if user has already got all badges
        return
    return min(n_actions_to_badge)


def user_inactivity_days(app, user):
    last_activity = TaskStatus.objects.filter(app_id=app, user_id=user).aggregate(Max('created_at'))['created_at__max']
    if last_activity:
        now = datetime.now(timezone.utc)
        diff = now - last_activity
        return diff.days
    else:
        return get_user_joining_date(user)


def last_issued_message_days(user_messages):
    datetime_list = [m['created'] for m in user_messages if m['delivered']]
    last_sent = max(datetime_list)
    delta = datetime.now(timezone.utc) - last_sent
    return delta.days


def send_incentive_message(user, app, incentive, user_messages, frequency, repeat, inactivity):
    days_inactivity = user_inactivity_days(app, user)
    if len(user_messages) > 0:
        # check the last time the user issued the incentive
        days_last_message = last_issued_message_days(user_messages)
    else:
        # getting the user inactivity from joining_date
        days_last_message = get_user_joining_date(user)

    if days_inactivity >= inactivity and days_last_message >= frequency and len(user_messages) < repeat:
        message_to_issue = Messages()

        if incentive.get('message').count('#'):  # whether there's a '#' for threshold counting
            n_actions = get_user_number_actions_left_for_badge(int(user), incentive['taskTypeId'], incentive['label'], app)
            if n_actions:  # Only if there are relevant badges yet to be asserted
                return message_to_issue.issue_for_real(incentive, user, app, n_actions)
        else:
            return message_to_issue.issue_for_real(incentive, user, app)  # In case of no threshold counting


def test_crone():
    logger.warning("---------------------- begins!")
    m = Complaint(app_id='test', user_id='test', content='test')
    m.save()
    print('sdadas')


def start():
    logger.warning("incentive messages process begins!")
    apps_list = list(WeNetApps.objects.all().values())
    apps_list = [app['app_id'] for app in apps_list]
    for app in apps_list:
        incentive_messages = [msg for msg in IncentiveMessages.objects.filter(app=app).values()]

        random.shuffle(incentive_messages)
        r = api_call(config_list['wenet_get_users_by_app'] % app, 'get')

        if r.status_code != 200:
            logger.error(f'Problems with getting app {app} users: {r.json()}')
            continue
        users = r.json()
        for user in users:
            email, cohort = insert_user_if_not_exist(user, app)
            # if not cohort:
            #    continue
            for incentive in incentive_messages:
                try:
                    if incentive.get('label') == 'noQuestions':
                        # Temporarily deleted constraint "taskTypeID" == "ask4help" because of dev's "6125f1f523db190661a28661"
                        if TaskStatus.objects.filter(app_id=app, user_id=user, label='nolabel!').count():  # Whether the user ever asked a question
                            continue

                    user_messages = list(IssuedIncentives.objects.filter(user_id=str(user), app_id=app,
                                                                         incentive_id=incentive.get('entityId'),
                                                                         delivered=1).values())

                    if incentive['inactivity_period']:
                        inactivity = incentive['inactivity_period']
                    else:
                        inactivity = random.randint(incentive['inactivity_range_bottom'], incentive['inactivity_range_top'])

                    repeat, frequency = incentive['max_repeat'], incentive['frequency']
                    
                    delivered = send_incentive_message(user, app, incentive, user_messages, frequency, repeat,
                                                       inactivity)
                    if delivered:
                        break
                except Exception as e:
                    logger.error(f'Problem creating message to a user {user} : {e}')
                    pass

    logger.info("incentive messages process finished successfully!")
    return 'incentive messages process finished successfully!'


# def start():
#    logger.warning("incentive messages process begins!")
#    apps_list = list(WeNetApps.objects.all().values())
#    apps_list = [app['app_id'] for app in apps_list]
#    for app in apps_list:
#        incentives_ids =[i['incentive_id'] for i in list(IncentiveApp.objects.filter(app_id=app).all().values())]
#        inventive_messages = [i.__dict__ for i in list(IncentiveMessages.objects.in_bulk(incentives_ids).values())]
#
#        random.shuffle(inventive_messages)
#        r = requests.get(config_list['wenet_get_users_by_app'] % app,
#                             headers={"x-wenet-component-apikey": os.environ.get('COMP_AUTH_KEY')})
#        if r.status_code != 200:
#            logger.error(f'Problems with getting app {app} users: {r.json()}')
#            continue
#        users = r.json()
#        for user in users:
#            email, cohort = insert_user_if_not_exist(user, app)
#            if not cohort:
#                continue
#            for incentive in inventive_messages:
#                if incentive.get('family_id') == 'base':
#                    try:
#                        user_messages = list(IssuedIncentives.objects.filter(user_id=str(user), app_id=app, incentive_id=incentive.get('id'), delivered=1).values())
#                        message_family = MessagesFamily.objects.filter(family='base').values()[0]
#                        frequency, repeat, inactivity = message_family['condition_frequency'], message_family['condition_repeat'], message_family['condition_inactivity']
#                        tags = [{tag['tag_name']:tag['tag_value']} for tag in list(MessageTag.objects.filter(incentive=incentive.get('id')).values())]
#                        tags = dict((key, d[key]) for d in tags for key in d)
#                        delivered = send_incentive_message(user, app, incentive, tags['QueryLabel'], tags['type'], user_messages, frequency, repeat, inactivity)
#                        if delivered:
#                            break
#                    except Exception as e:
#                        logger.error(f'Problem creating message to a user {user} : {e}')
#                        pass
#    logger.info("incentive messages process finished successfully!")
#    return 'incentive messages process finished successfully!'


def is_post_incentive_message_valid(data):
    if (not type(data.get('taskTypeId')) is str) or (not type(data.get('app')) is str):
        return respond_json("'taskTypeId' and 'app' are required and must be non-null strings", 400)

    if (not type(data.get('max_repeat')) is int or data['max_repeat'] < 1) or \
            (not type(data.get('frequency')) is int or data['frequency'] < 1):
        return respond_json("'max_repeat and 'frequency' are required and must be positive integers", 400)

    if data.get('inactivity_period'):
        if not type(data.get('inactivity_period')) is int or data.get('inactivity_period') < 1:
            return respond_json("'inactivity_period', if inserted, must be a positive integers", 400)
        if data.get('inactivity_range_top') or data.get('inactivity_range_bottom'):
            return respond_json("Please fill either 'inactivity_period' or both 'inactivity_range_top' and 'inactivity_range_bottom' - not all three", 400)
    if (data.get('inactivity_range_top') and not data.get('inactivity_range_bottom')) or (not data.get('inactivity_range_top') and data.get('inactivity_range_bottom')):
        return respond_json("If you filled either 'inactivity_range_top' or 'inactivity_range_bottom' - please fill the other as well", 400)
    if data.get('inactivity_range_top') and data.get('inactivity_range_bottom'):
        if not type(data.get('inactivity_range_top')) is int or not type(data.get('inactivity_range_bottom')) is int or data.get('inactivity_range_top') < 1 or data.get('inactivity_range_bottom') < 1:
            return respond_json("'inactivity_range_top' and 'inactivity_range_bottom', if inserted, must be positive integers", 400) 
        if data.get('inactivity_range_top') <= data.get('inactivity_range_bottom'):
            return respond_json("'inactivity_range_top' must be greater than 'inactivity_range_bottom'", 400)
    # default fill
    if not data.get('inactivity_period') and not data.get('inactivity_range_top') and not data.get('inactivity_range_bottom'):
        data['inactivity_range_top'] = 5
        data['inactivity_range_bottom'] = 3

    if data.get('label', '!no!') in ['!no!', None, '']:
        data['label'] = 'nolabel!'
    if not type(data['label']) is str:
        return respond_json("'label' field, if this message is for a TaskTransaction, must be a non-null string", 400)

    # threshold counting 'message' field - applied when no 'message' field is inserted
    if data.get('message', '!no!') in ['!no!', None, '', 'None', 'null']:
        if data['label'] == 'nolabel!':
            data['message'] = f"You are # ({data['taskTypeId']})s away from a new badge!"
        else:
            data['message'] = f"You are # ({data['label']})s away from a new badge!"
    if not type(data['message']) is str or data['message'].count('#') > 1:
        return respond_json("'message' field must be a string and include no more than a single '#' for threshold counting", 400)

    if len(list(IncentiveMessages.objects.filter(taskTypeId=data.get('taskTypeId'),
                                                 label=data.get('label'),
                                                 app=data.get('app'),
                                                 message=data.get('message')).all().values())) > 0:
        return respond_json("Duplicate Incentive Message POST aborted - existing combination of 'app', 'taskTypeId', 'label' and 'message' fields", 400)
 

    return data


def get_incentive_message_detial(msg):
    try:
        msg = msg[0]
        msg['createdAt']=str(msg['createdAt'])
        del msg['id']
        del msg['entityId']
        if msg['label'] == 'nolabel!':
            del msg['label']
        if not msg.get('inactivity_period'):
            del msg['inactivity_period']
        else:
            del msg['inactivity_range_top']
            del msg['inactivity_range_bottom']

        r = {'IncentiveMessage': msg,
             "status_code": 200
             }
        return msg
    except IndexError:
        return None

def get_incentive_message_valid(msg):
    msg_detial= get_incentive_message_detial(msg)
    if msg_detial!=None:
        r = {'IncentiveMessage': msg_detial,
            "status_code": 200
            }
        return JsonResponse(r, status=200)
    else:
        return respond_json("Incentive Message not found - Invalid entityId", 404)


# def get_incentive_message_valid(msg):
#     try:
#         msg = msg[0]
#         del msg['id']
#         del msg['entityId']
#         if msg['label'] == 'nolabel!':
#             del msg['label']
#         if not msg.get('inactivity_period'):
#             del msg['inactivity_period']
#         else:
#             del msg['inactivity_range_top']
#             del msg['inactivity_range_bottom']

#         r = {'IncentiveMessage': msg,
#              "status_code": 200
#              }
#         return JsonResponse(r, status=200)
#     except IndexError:
#         return respond_json("Incentive Message not found - Invalid entityId", 404)

def all_issued():
    issued= IssuedIncentives.objects.all().values()
    return  issued

def put_incentive_message(entityId, data, msg):
    def invalid_field(field):
        return respond_json(f"Validation Error - Invalid field in body request: {field}", 400)

    msg = msg[0]
    updatedFields = {}

    if data.get('taskTypeId') and data.get('taskTypeId') != '':
        if not type(data.get('taskTypeId')) == str:
            return invalid_field('taskTypeId')
        if msg['taskTypeId'] != data['taskTypeId']:
            updatedFields['taskTypeId'] = data['taskTypeId']

    if msg['label'] == 'nolabel!' and not data.get('label') in [None, '',
                                                                'nolabel!']:  # if IM is of TaskType - it is irreversible
        return respond_json(
            "TaskType IncentiveMessage cannot be altered into a TaskTransaction IncentiveMessage",
            400)

    if msg['label'] != 'nolabel!' and data.get(
            'label') == 'nolabel!':  # if IM is of TaskTransaction - it is irreversible
        return respond_json(
            "TaskTransaction IncentiveMessage cannot be altered into a TaskType IncentiveMessage",
            400)

    if msg['label'] != 'nolabel!':  # if IM is of TaskType - it is irreversible
        if data.get('label') and data.get('label') != '':
            if not type(data.get('label')) == str:
                return invalid_field('label')
            if msg['label'] != data['label']:
                updatedFields['label'] = data['label']

    if (data.get('max_repeat') or data.get('max_repeat') == 0) and data.get('max_repeat') != '':
        if not type(data.get('max_repeat')) == int or data.get('max_repeat') < 1:
            return invalid_field('max_repeat')
        if msg['max_repeat'] != data['max_repeat']:
            updatedFields['max_repeat'] = data['max_repeat']

    if (data.get('frequency') or data.get('frequency') == 0) and data.get('frequency') != '':
        if not type(data.get('frequency')) == int or data.get('frequency') < 1:
            return invalid_field('frequency')
        if msg['frequency'] != data['frequency']:
            updatedFields['frequency'] = data['frequency']

    if data.get('inactivity_period'):
        if not type(data.get('inactivity_period')) is int or data.get('inactivity_period') < 1:
            return respond_json("'inactivity_period', if inserted, must be a positive integers", 400)
        if data.get('inactivity_range_top') or data.get('inactivity_range_bottom'):
            return respond_json("Please fill either 'inactivity_period' or both 'inactivity_range_top' and 'inactivity_range_bottom' - not all three", 400)
        if msg['inactivity_period'] != data['inactivity_period']:
            updatedFields['inactivity_period'] = data['inactivity_period']
            updatedFields['inactivity_range_top'] = None
            updatedFields['inactivity_range_bottom'] = None

    if (data.get('inactivity_range_top') and not data.get('inactivity_range_bottom')) or (not data.get('inactivity_range_top') and data.get('inactivity_range_bottom')):
        return respond_json("If you filled either 'inactivity_range_top' or 'inactivity_range_bottom' - please fill the other as well", 400)
    if data.get('inactivity_range_top') and data.get('inactivity_range_bottom'):
        if not type(data.get('inactivity_range_top')) is int or not type(data.get('inactivity_range_bottom')) is int or data.get('inactivity_range_top') < 1 or data.get('inactivity_range_bottom') < 1:
            return respond_json("'inactivity_range_top' and 'inactivity_range_bottom', if inserted, must be positive integers", 400) 
        if data.get('inactivity_range_top') <= data.get('inactivity_range_bottom'):
            return respond_json("'inactivity_range_top' must be greater than 'inactivity_range_bottom'", 400)
        if msg['inactivity_range_top'] != data['inactivity_range_top']:
            updatedFields['inactivity_range_top'] = data['inactivity_range_top']
            updatedFields['inactivity_period'] = None
        if msg['inactivity_range_bottom'] != data['inactivity_range_bottom']:
            updatedFields['inactivity_range_bottom'] = data['inactivity_range_bottom']
            updatedFields['inactivity_period'] = None

    if data.get('app') and data.get('app') != '':
        if not type(data.get('app')) == str:
            return invalid_field('app')
        if msg['app'] != data['app']:
            updatedFields['app'] = data['app']

    if data.get('message') and data.get('message') != '':
        if not type(data.get('message')) == str or data['message'].count('#') > 1:
            return respond_json("'message' field must be a string and include no more than a single '#' for threshold counting", 400)

        if msg['message'] != data['message']:
            updatedFields['message'] = data['message']

    return updatedFields




class Messages(Incentive):


    def issue_for_real(self, incentive, user_id, app_id, n_actions=None):
        try:
            message = incentive.get('message')
            if n_actions:
                message = message.replace('#', str(n_actions))

            data_wenet = {
                "AppID": app_id,
                "UserId": str(user_id),
                "Issuer": "WeNet issuer",
                "IncentiveType": "Message",
                "Message": {"content": message}

            }
            # posting the incentive to wenet platform
            r = api_call(config_list['url_wenet_post_incentive'], 'post', data_wenet)

            # log the issued incentive into dedicated table
            if r.status_code == 202:
                delivered = 1
            else:
                delivered = 0
                logger.error(f"The user was not notified: {r.content} about the message :{message}")
            issued_incentive = {
                "app_id": app_id,
                "user_id": user_id,
                "incentive_id": incentive.get('entityId'),
                "type": 'message',
                "delivered": delivered
            }
            self.insert_issued_incentive(IssuedIncentives, issued_incentive)
            return delivered

        except Exception as e:
            logger.error(f'error occured when tried to issue incentive message: {r.content}')

            return e.__dict__

# def issue_for_real(self, incentive, user_id, app_id, extra=None):
#    try:
#        message = incentive.get('message')
#        if extra:
#            a, b = message.splitlines()
#            message = f'{a} {extra} {b}'
#        data_wenet = {
#            "AppID": app_id,
#            "UserId": str(user_id),
#            "Issuer": "WeNet issuer",
#            "IncentiveType": "Message",
#            "Message": {"content": message}

#        }
#        # posting the incentive to wenet platform

#        r = requests.post(
#            config_list['url_wenet_post_incentive'], data=json.dumps(data_wenet),
#            headers={"Content-Type": "application/json", "x-wenet-component-apikey": os.environ.get('COMP_AUTH_KEY')})
#        # log the issued incentive into dedicated table
#        if r.status_code == 202:
#            delivered = 1
#        else:
#            delivered = 0
#            logger.error(f"The user was not notified: {r.content} about the message :{message}")
#        issued_incentive = {
#            "app_id": app_id,
#            "user_id": user_id,
#            "incentive_id": incentive.get('id'),
#            "type": 'message',
#            "delivered": delivered
#        }

#        self.insert_issued_incentive(IssuedIncentives, issued_incentive)
#        return delivered

#    except Exception as e:
#        logger.error(f'error accord when issued incentive message: {r.content}')

#        return e.__dict__

