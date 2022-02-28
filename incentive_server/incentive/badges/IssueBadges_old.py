import json
import requests
import numpy as np


from incentive.config.Config import Config
Config = Config()
config_list = Config.get_config()
relations_badges = Config.get_relations_badges()
touch_badges = Config.get_touch_badges()

import sys
sys.path.append('../')
from incentive.models import IssuedIncentives




def get_badge_details(badge_id):
    response = requests.get(config_list['url_badgr'] + config_list['get_badge_class'] % badge_id,
                            headers={"Authorization": "Token " + config_list['badgr_token'],
                                     "Content-Type": "application/json"})
    content = json.loads(response.content)
    message = content['result'][0]['description']
    criteria = content['result'][0]['criteriaNarrative']
    return message, criteria


# def is_got_badge(user_email, badge_id):
#     response = requests.get(config_list['url_badgr'] + config_list['url_badgeClass_assertions'] % badge_id
#                             , headers={"Authorization": "Token %s" % config_list['badgr_token'],
#                                        "Content-Type": "application/json"})
#     content = json.loads(response.content)
#     got_badge = 0
#     for result in content['result']:
#
#         if user_email == result['recipient']['plaintextIdentity']:
#             got_badge = 1
#     return got_badge


def issue_for_real(user, badge_id):
    # issue the badge on badgr server
    data_badgr = {
        "recipient": {
            "identity": user.email,
            "type": "email",
            "hashed": 'true'
        },
        "notify": 'true',
        "evidence": [
            {
                "narrative": "This is a narrative describing the individual evidence item."
            }
        ]
    }

    response = requests.post(
        config_list['url_issue_badge'] % badge_id, data=json.dumps(data_badgr),
        headers={"Content-Type": "application/json"})
    # posting the incentive to wenet platform
    try:
        content = json.loads(response.content)
        message, criteria = get_badge_details(badge_id)
        data_wenet = {
            "AppID": user.app_id,
            "UserId": user.user_id,
            "Issuer": "WeNet issuer",
            "IncentiveType": "Badge",
            "Badge": {
                "BadgeClass": badge_id,
                "ImgUrl": content['result'][0]['image'],
                "Criteria": criteria,
                "Message": message
            }

        }
        requests.post(
            config_list['url_wenet_post_incentive'], data=json.dumps(data_wenet),
            headers={"Content-Type": "application/json"})
        # log the issued incentive into dedicate table
        issued_incentive = {
            "app_id": user.app_id,
            "UserId": user.user_id,
            "incentive_id": badge_id,
            "type": 'badge'
        }
        self.insert_issued_incentive(IssuedIncentives,issued_incentive)
        return issued_incentive
    except Exception as e:
        # need to log into file
        return response
    return response


def issue(user, str_type):
    if str_type == 'relations':
        for name, value in relations_badges['badges'].items():
            if np.logical_and(user.relations >= value,
                              is_got_badge(user.email, relations_badges['badges_id'][name])):
                return issue_for_real(user.email, relations_badges['badges_id'][name], user.user_id, user.app_id)
    else:
        for name, value in touch_badges['badges'].iteritems():
            if np.logical_and(user.diaries_answers >= value,
                              is_got_badge(user.email, touch_badges['badges_id'][name]) == 0):
                return issue_for_real(user, touch_badges['badges_id'][name])
