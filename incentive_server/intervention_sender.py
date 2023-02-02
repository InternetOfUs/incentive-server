import time
import uuid
import requests
import datetime
# from Predictor.Config.Config import Config

ACCESS_TOKEN_URL = 'https://signin.zooniverse.org/oauth/token'
MESSAGES_API_URL = 'https://interventions-gateway.zooniverse.org/messages'
ALL_AUDIENCES = "user project group collection classification subject medium organization  translation public"
# AUDIENCES = "user project public"
# CLIENT_ID = "598c501f0268bfac7efa29b83404b10b449e79f0e08aabebdbcdc26606223c42"
# CLIENT_SECRET = "b2b462efc3082fb735f07ab0071ffb7253d6b64992bce1b9909547af776ae6a5"

GALAXY_ZOO_APP_ID = "52e311605d7c703b744232ddbe12bd40f2986a0ae75250a03894b6cdedaba30b"
GALAXY_ZOO_SECRET = "48f91d50ce123f15e0dd11231b622071f52778473563d9afef3009031983c9ca"
MY_USER_ID = 1838149
MY_TEST_PROJECT_ID = 7800
GALAXY_ZOO_PROJECT_ID = 5733
# config = Config.conf

# todo: get credentials for all projects.


TOKEN = None
TOKEN_EXPIRY_TIME = datetime.datetime.now()


class RequestFailedException(Exception):
    pass


def _regenerate_token():
    global TOKEN
    global TOKEN_EXPIRY_TIME
    oauth2_headers = {
        'content-type': 'application/json',
    }

    oauth2_data = {
        "grant_type": "client_credentials",
        "client_id": GALAXY_ZOO_APP_ID,
        "client_secret": GALAXY_ZOO_SECRET,
        "audience": ALL_AUDIENCES
    }
    response_data = _send_request(ACCESS_TOKEN_URL, oauth2_headers, oauth2_data)
    TOKEN = '{} {}'.format(response_data['token_type'], response_data['access_token'])
    expires_in_seconds = response_data['expires_in']
    token_created_time = datetime.datetime.now()
    TOKEN_EXPIRY_TIME = token_created_time + datetime.timedelta(
        seconds=expires_in_seconds - 120)  # 2 minutes safety delta


def _send_request(url, headers, data, tries=3):
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        return response.json()
    else:
        if tries:
            time.sleep(5)
            _send_request(url, headers, data, tries=tries - 1)
        else:

            raise RequestFailedException('request failed ({}): {}. url: {}, headers: {},'
                                         'payload: {}'.
                                         format(response.status_code, response.text, url, headers, data))


def send_intervention(project_id, intervention_text, user_id, retries=3, production=True, logger=None):
    if datetime.datetime.now() > TOKEN_EXPIRY_TIME:
        _regenerate_token()
        if logger:
            logger.info("generated oauth token")

    headers = {
        'Authorization': TOKEN,
        'Content-Type': 'application/json',
    }

    data = {
        "project_id": str(project_id),
        "user_id": str(user_id),
        "message": intervention_text,
        # "workflow_id": config['experiment_workflow_id']
    }

    if production:
        response = _send_request(MESSAGES_API_URL, headers, data, tries=retries)
        if logger:
            logger.info("request sent. response: {}".format(response))
    return uuid.uuid4().int


# print send_intervention(project_id=GALAXY_ZOO_PROJECT_ID,
#                         intervention_text="hello hello hello hello hello ", user_id=MY_USER_ID, retries=0)
