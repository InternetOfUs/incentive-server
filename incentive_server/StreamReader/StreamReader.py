#!/usr/bin/env python
from os.path import dirname
import requests
import json
import sys
import time
# import pusherclient
# import MySQLdb
import pymysql

import datetime
from Config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

src_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(src_dir)
from utils.utils import err

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
log_formatter.converter = time.gmtime
cnf = Config.Config().conf

root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
root.addHandler(ch)
ch.setLevel(logging.WARNING)
root.setLevel(logging.INFO)

logFile = cnf['strmLog']
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=1 * 1024 * 1024, backupCount=50, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.WARNING)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

global pusher


class Classification:
    def __init__(self, participating_experiment):
        self.participating_experiment = participating_experiment



def sql(user_id, city_name, country_name, project_id, subjects, created_at, is_experiment_user=False):
    local_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    conn = pymysql.connect(host=cnf['host'], user=cnf['user'], passwd=cnf['password'], db=cnf['db'])
    conn.autocommit(True)

    cursor = conn.cursor()
    try:

        if is_experiment_user:
            app_log.warn(" inserting a new record: {} {} {} {} {} {} {}".format(
                user_id, project_id, subjects, created_at, country_name, city_name, local_time,))

            cursor.execute(
                """INSERT INTO stream
                (user_id, project   , subjects, created_at, country_name, city_name, local_time) 
                VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (user_id, project_id, subjects, created_at, country_name, city_name, local_time)
            )
        else:

            non_experiment_user_cohort_id = 0
            non_experiment_user_intervention_id = "None"

            app_log.warn(" inserting a new record: {} {} {} {} {} {} {} {} {}".format(
                user_id, project_id, subjects, created_at, country_name, city_name, local_time,
                non_experiment_user_cohort_id, non_experiment_user_intervention_id))

            cursor.execute(
                """INSERT INTO stream
                (user_id, project   , subjects, created_at, country_name, city_name, local_time,cohort_id, intervention_id) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (user_id, project_id, subjects, created_at, country_name, city_name, local_time,
                 non_experiment_user_cohort_id, non_experiment_user_intervention_id)
            )
        conn.commit()

    except pymysql.Error as e:
        err(app_log, e)
        conn.rollback()
    conn.close()


def filter_classifications(data):
    project_id = data['project_id']
    user_id = data['user_id']
    workflow_id = data['workflow_id']
    if user_id is not None:
        if project_id == str(cnf['project_id_to_listen']):  # galaxy zoo project id
            if workflow_id == cnf['experiment_workflow_id']:
                app_log.warn('got data from project: {}'.format(data))
                return Classification(participating_experiment=True)
            else:
                return Classification(participating_experiment=False)


def channel_callback(json_data):
    now = datetime.datetime.now()
    data = json_data
    classification = filter_classifications(data)

    if classification:
        app_log.warn('caught channel callback')

        try:
            project_id = data['project_id']
            user_id = data['user_id']
            country_name = data['geo']['country_name']
            city_name = data['geo']['city_name']
            subject_ids = data['subject_ids']

            sql(user_id, city_name, country_name, project_id, subject_ids, now,
                is_experiment_user=True)
            app_log.warn("{}Participating in the experiment- user_id: {}. Record added.".format(
                "" if classification.participating_experiment else "Not ", user_id))

        except Exception as e:
            err(app_log, e)


def connect_handler(_):
    app_log.warn('caught connection')
    channel = pusher.subscribe("panoptes")
    channel.bind('classification', channel_callback)

def get_fake_srteam():
    url = cnf['fake_Stream_url']
    data = requests.get(url).json()
    channel_callback(data)
if __name__ == "__main__":
    while True:
        try:
            get_fake_srteam()
            # app_log.warn("starting stream")
            # appkey = "79e8e05ea522377ba6db"    # Production
            # pusher = pusherclient.Pusher(appkey)
            # pusher.connection.bind('pusher:connection_established', connect_handler)
            # pusher.connect()
            #
            # while True:
            #     time.sleep(3)
            #     if pusher.connection.state != "connected":
            #         app_log.warn("pusher state is:" + pusher.connection.state + "\n")
            #         pusher.disconnect()
            #         time.sleep(2)
            #         break
        except Exception as ex:
            err(app_log, ex)
        continue
