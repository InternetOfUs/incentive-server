from django.test import TestCase
import random
inc_status = True
# Create your tests here.

# import urllib, urllib2, cookielib
#
# # do POST
# url_2 = 'http://127.0.0.1:8000/incentives'
# headers={'Authorization':'Token fd8dfa28ee89fea2413f3232fe3162423a4da594 '}
# values = dict(schemeID='1')
# data = urllib.urlencode(values)
# req = urllib2.Request(url_2, data,headers=headers)
# rsp = urllib2.urlopen(req)
# content = rsp.read()
#
# # print result
# import re
# pat = re.compile('Title:.*')
# print pat.search(content).group()


def check_user(user_id):
    return True


def check_app(app_id):
    if app_id == "I2AFRCOXx3":
        return True
    return False


def check_community(community_id):
    rand = random.random()
    return rand <= 0.7


def check_inc_status(community_id):
    if inc_status:
        return True
    else:
        return False

