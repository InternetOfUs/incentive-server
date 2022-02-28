import sys
import time
from os.path import dirname
# import MySQLdb
import pymysql

import os
import datetime
import logging
from logging.handlers import RotatingFileHandler
from contextlib import closing

# enable project imports
src_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(src_dir)

from Config.Config import Config
from utils.utils import err, get_stream_latest_id, mysql_connect

from dis_predictor import dis_predictor
from intervention_sender import send_intervention

config = Config().conf

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
log_formatter.converter = time.gmtime

root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
root.addHandler(ch)
ch.setLevel(logging.INFO)
root.setLevel(logging.INFO)

logFile = config['predLog']
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=1 * 1024 * 1024, backupCount=50, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

prev_hour = datetime.datetime.now().hour


def sql(query, params):
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db=config['db'])
    with closing(conn.cursor()) as cursor:
        try:
            cursor.execute(query, params)
            conn.commit()
        except pymysql.Error as e:
            app_log.info("Unable to connect to DB.")
            err(app_log, e)
            conn.rollback()


def sql_get(query, params):
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db=config['db'])
    rows = None
    with closing(conn.cursor()) as cursor:
        try:
            cursor.execute(query, params)
            conn.commit()
            rows = cursor.fetchall()
        except pymysql.Error as e:
            err(app_log, e, "Unable to connect to DB")
            conn.rollback()
        except pymysql.ProgrammingError as ex:
            if cursor:
                err(app_log, ex, "\n".join(cursor.messages))
                # You can show only the last error like this.
                # print cursor.messages[-1]
            else:
                err(app_log, ex, "\n".join(conn.messages))
                # Same here you can also do.
                # print self.db.messages[-1]
            conn.rollback()
    return rows


def main():
    try:
        # global Alg
        Alg = dis_predictor()
        app_log.info("Algorithm initialization successful.")
        import requests.packages.urllib3
        requests.packages.urllib3.disable_warnings()
    except Exception as e:
        err(app_log, e, "Error, unable to start algorithm.")
        app_log.info(os.getcwd())
        return

    while True:
        try:
            app_log.info("Ready")
            prediction_loop(Alg)
        except Exception as e:
            err(app_log, e, "Prediction Loop failed.")
            continue


def log_im_alive():
    global prev_hour
    now = datetime.datetime.now()
    if now.hour > prev_hour and now.minute == 0:
        app_log.info("Predictor is alive at {}".format(now.strftime('%Y-%m-%d %H:%M:%S')))
        prev_hour = now.hour


def prediction_loop(Alg):
    local_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    conn = mysql_connect(**config)
    app_log.info("mysql connected.")
    app_log.info("predicting for everything after %s" % local_time)
    latest_id = get_stream_latest_id(conn.cursor())

    while True:
        try:
            log_im_alive()
            sql("""update stream set intervention_id=%s where user_id=%s""", ("-1", "Not Logged In"))

            rows = sql_get(
                """SELECT id,user_id,created_at,project
                FROM stream
                WHERE intervention_id IS NULL and id>=%s""",
                [latest_id]
            )

            for row in rows:
                try:
                    row_id = row[0]
                    user_id = row[1]
                    created_at = row[2]
                    project_id = int(row[3])
                    app_log.info("Making a decision about user_id: {}, project_id: {}".format(user_id, project_id))

                    if user_id == "Not Logged In":  # todo consider removing this, user id NOT NULL?
                        continue

                    created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
                    incentive = Alg.intervene(user_id, created_at)
                    preconfigured_id, cohort_id, algo_info = incentive[0], incentive[1], incentive[2]
                    app_log.info("Decision made: {}".format(preconfigured_id))

                    if preconfigured_id > 0:
                        production = config['production']
                        app_log.info("sending intervention num {} to user {}".format(preconfigured_id, user_id))
                        intervention_id = send_intervention_for_user(
                            user_id, preconfigured_id, project_id, production=production)
                    else:
                        intervention_id = "None"

                    app_log.info(
                        "Updating: user_id: {}, intervention_id: {}, preconfigured_id:{} cohort_id: {}".format(
                            user_id, intervention_id, preconfigured_id, cohort_id))
                    sql(
                        """update stream
                        set preconfigured_id=%s,
                        cohort_id=%s,
                        algo_info=%s,
                        intervention_id=%s
                        where id=%s""",
                        (preconfigured_id, cohort_id, algo_info, intervention_id, row_id))

                    app_log.info("done execute")
                except Exception as e:
                    err(app_log, e)
                    sql("update stream set intervention_id=%s where id=%s", ("Failed", row[0]))
                    continue
        except Exception as e:
            err(app_log, e, "Error2")
            continue


def send_intervention_for_user(user_id, preconfigured_id, project_id, production=True):
    try:
        intervention_text = config['interventions_id_to_text'][preconfigured_id]
        return 5
    except Exception as e:
        err(app_log, e)


if __name__ == "__main__":
    app_log.info("---------starting Predictor---------")
    main()
