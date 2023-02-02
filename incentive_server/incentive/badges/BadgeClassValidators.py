import os, json, requests, base64, shutil
# from urllib.request import urlretrieve
from urllib.error import HTTPError
import http.client
from django.http.response import HttpResponseBadRequest
from django.http import JsonResponse
from .Badges import get_badge_details_from_response
from incentive.helper import respond_json, api_call
from incentive.config.Config import Config

Config = Config()
config_list = Config.get_config()


def check_image_url(imageUrl):
    if not imageUrl[4] in ['s','S']:  # not HTTPS
        return respond_json('Only HTTPS URLs are allowed', 403)

    if not imageUrl[-4:] in [".png", ".svg"]:  # badgr accepts .png only
        return respond_json('URL must end with .png or .svg', 403)

    try:
        r = requests.get(imageUrl, stream=True)
        if r.status_code == 200:
            with open("image.png", 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        elif r.status_code == 404:
            return respond_json('URL not found', 403)
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema, requests.exceptions.SSLError):
        return respond_json('An invalid URL was posted', 403)

    return f"data:image/png;base64,{base64.b64encode(open('image.png', 'rb').read()).decode('utf-8')}"




def getBadgeClass(entityId):
    response = api_call(config_list['url_badgr'] + 'v2/badgeclasses/' + entityId, 'get')

    if response.status_code == 500:
        return HttpResponseBadRequest(response)

    if response.status_code == 404:
        return respond_json('BadgeClass not found - Invalid entityId', 404)

    if response.status_code == 200:
        badge = get_badge_details_from_response(response.json().get('result')[0])
        if badge.get('label', 0) in ['nolabel!', '', 'None', 'none', 'null', 'Null', None]:
            del badge['label']  # TaskTypeBadgeClass - no label
        return {'badge': badge}


def putBadgeClass(data, badge):
    # 'taskTypeId' and 'label' fields cannot be updated.
    updatedFields = {}

    if data.get('name') and data.get('name') != '':
        if badge['name'] != data['name']:
            updatedFields['name'] = data['name']
    else:
        data['name'] = badge['name']  # badgr does not accept a null name

    if data.get('description') and data.get('description') != '':
        if badge['description'] != data['description']:
            updatedFields['description'] = data['description']
    else:
        data['description'] = badge['description']  # badgr does not accept a null description

    if data.get('message') and data.get('message') != '':
        if badge['message'] != data['message']:
            updatedFields['message'] = data['message']
    else:
        data['message'] = badge['message']  # Interaction Protocol does not accept a null message
    data['criteriaNarrative'] = data['message']  # required in badgr

    if data.get('taskTypeId') and data.get('taskTypeId') != '':
        if badge['taskTypeId'] != data['taskTypeId']:
            updatedFields['taskTypeId'] = data['taskTypeId']
    else:
        data['taskTypeId'] = badge['taskTypeId']

    if badge.get('label'):  # only for TaskTransactionBadgesClasses
        if data.get('label') and data.get('label') != '':
            if badge['label'] != data['label']:
                updatedFields['label'] = data['label']
        else:
            data['label'] = badge['label']

    if data.get('threshold') and data.get('threshold') != '':
        if data['threshold'] < 1:
            return respond_json('Validation Error - Invalid field in body request: threshold must to be a positive integer', 400)
        if badge['threshold'] != data['threshold']:
            updatedFields['threshold'] = data['threshold']
    else:
        data['threshold'] = badge['threshold']

    if data.get('image') and data.get('image') != '':
        if badge['image'] != data['image']:
            checked_image_url = check_image_url(data['image'])
            if type(checked_image_url) is JsonResponse:  # imageUrl 403 Error
                return respond_json(f'Validation Error - Invalid field in body request: {json.loads(checked_image_url.content.decode("utf-8")).get("message")}', 400)
            updatedFields['image'] = data['image']
            imageUrl = data['image']
            data['image'] = checked_image_url  # encoded

        else:
            imageUrl = data['image']
            data['image'] = check_image_url(data['image'])  # encoded

    else:
        imageUrl = badge['image']
        data['image'] = check_image_url(badge['image'])  # encoded

    if data.get('app') and data.get('app') != '':
        if badge['app'] != data['app']:
            updatedFields['app'] = data['app']
    else:
        data['app'] = badge['app']

    if not badge.get('label'): #  for TaskTypeBadgeClasses
        data['label'] = 'nolabel!'
    data['tags'] = [f'taskTypeId {data["taskTypeId"]}', f'label {data["label"]}', f'threshold {data["threshold"]}',
                    f'app {data["app"]}', f'imageUrl {imageUrl}']
    return data, updatedFields


def revokeBadgeClassAssertions(entityId):
    # GET list of BadgeClass's assertions
    get_response = api_call(config_list['url_badgr'] + 'v2/badgeclasses/%s/assertions' % entityId, 'get')

    if get_response.status_code == 500:
        return HttpResponseBadRequest(get_response)

    if get_response.status_code != 200:
        return respond_json("Problem getting the list of the desired BadgeClass's assertions", get_response.status_code)

    # DELETE all assertion of the desired BadgeClass
    for assertion in get_response.json().get('result'):
        assertion_id = assertion['entityId']
        assert_del_response = api_call(config_list['url_badgr'] + 'v2/assertions/' + assertion_id, 'delete', {"revocation_reason": "DELETE BadgeClass"})

        if assert_del_response.status_code == 500:
            return HttpResponseBadRequest(assert_del_response)
