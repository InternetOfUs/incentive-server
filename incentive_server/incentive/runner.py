import json
import numpy as np
import numpy
import sys
import logging
import datetime
import traceback
from json import JSONEncoder
# from sklearn.externals import joblib
import joblib
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from django.views.decorators.csrf import csrf_exempt

from intervention_sender import send_intervention
from Config.Config import Config
from utils.utils import err
__author__ = 'Daniel'

config = Config.conf

log = logging.getLogger(__name__)

Alg = None


@csrf_exempt
def startAlg(request):
    # note - this is not the usage
    try:
        global Alg
        Alg = dis_predictor()
        return JSONResponse(json.dumps('{"Alg": "Success"}'))
    except Exception as e:
        trace = traceback.format_exc()
        d = {"Alg": "Success", "error": str(e), "traceback": str(trace)}
        response = json.dumps(d)
        return JSONResponse(d)


@csrf_exempt
def getTheBestForTheUser(request, userID, created_at):
    global Alg
    try:
        incentive = Alg.predicting(userID, created_at)
        if incentive[0] == 1:
            intervention_id = send_intervention_for_user(userID)
            json_incentive = JSONEncoder().encode({
                "userID": str(userID),
                "message": "Intervention sent, intervention id: "+intervention_id
            })

        else:
            json_incentive = '{"userID":"' + str(userID) + '","message":" Staying"}'

        return JSONResponse(json_incentive)
    except:
        return JSONResponse('{"Alg":"Error"}')


@csrf_exempt
def GiveRatio(request):
    global Alg
    try:
        l, s = Alg.disratio()
        ratio = []
        ratio.append("{\"l\":" + str(l) + ",\"s\":" + str(s) + "}")
        jsonIncentive = json.dumps(ratio)
        return JSONResponse(jsonIncentive)
    except:
        return JSONResponse('{"Alg":"Error"}')


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def send_intervention_for_user(userId):

    # todo understand why text is hard coded here
    # todo understand how to get project name here
    galaxy_zoo_id = 5733
    try:
        return 5
    except Exception as e:
        err(logging.getLogger(), e)
    # with requests.Session() as c:
    #     url = "http://experiments.zooniverse.org/users/" + userId + "/interventions"
    #     payload = {
    #         "project": "galaxy_zoo",
    #         "intervention_type": "prompt user about talk",
    #         "text_message": "please return",
    #         "cohort_id": 1,
    #         "time_duration": 60,
    #         "presentation_duration": 20,
    #         "intervention_channel": "web model",
    #         "take_action": "after_next_classification"
    #     }
    #
    #     request = c.post(url, data=payload)
    #     #print 'send_intervention_for_user(' + userId + '):' + request.content
    #     try:
    #         content = json.loads(request.content)
    #         intervention_id = content['id']
    #         print 'SUCCESS send_intervention_for_user(' + userId + '):'+intervention_id
    #         return intervention_id
    #     except:
    #         print 'ERROR: send_intervention_for_user(' + userId + '):'
    #         return "-1"


# def Pusher(userId, projectID, cohort_id, preconfigured_id, text_message, intervention_channel):
#     with requests.Session() as c:
#         url = "http://experiments.zooniverse.org/users/" + userId + "/interventions"
#         payload = {
#             'project': projectID,
#             'intervention_type': 'interrupt',
#             'cohort_id': cohort_id,
#             'preconfigured_id': preconfigured_id,
#             'text_message': text_message,
#             'intervention_duration': '0',
#             'intervention_channel': intervention_channel,
#             'take_action': 'immediately',
#         }
#
#         request = c.post(url, data=payload)
#         print (request.content)


class dis_predictor:
    def median(self, lst):
        return numpy.median(numpy.array(lst))

    def avg(self, lst):
        return numpy.average(numpy.array(lst))


    def __init__(self):

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
        logging.info("Loading and Initializing  Model")

        self.y_leaving = 0.
        self.y_staying = 0.
        self.running_uid = 0
        self.user_dict = {}
        self.user_past_session_time = []  # session0_time, session1_time, session2_time ...
        self.user_past_session_dwell_time = []  # session0_dwell_time, session1_dwell_time, session2_dwell_time ...
        self.user_past_tasks = []  # session0_tasks, session1_tasks, session2_tasks, ....
        self.user_current_session_stats = []  # timestamp_of_previous_task_in_this_session, this_sessions_tasks_count, this session_dwell_time, this_session_min_dwell_time, this_session_time
        self.user_past_session_stats = []  # past_sessions_count, total_tasks_count, total_sessions_time, total_dwell_time
        #'/home/eran/Documents/Lassi/src/Algorithem/Model/dismodel.pkl'
        #'/home/ise/Model/dismodel.pkl'
        # todo understand what is that model
        self.clf = joblib.load(config['clfFile'])
        logging.info("Finished Loading  Model")

    def fe(self, user_id_str, cteated_at_str):
        user_sid = user_id_str
        created_at = datetime.datetime.strptime(cteated_at_str, '%Y-%m-%d %H:%M:%S')
        pscountidx = 0;
        ptasksidx = 1;
        pstimeidx = 2;
        pdwellidx = 3
        clastseenidx = 0;
        ctaskidx = 1;
        cdwellidx = 2;
        cmdwellidx = 3;
        csstartidx = 4

        # get integer user_id from dictionary or create new if non existent
        if user_sid not in self.user_dict:  # first time encountering user
            self.user_dict[user_sid] = self.running_uid
            user_id = self.running_uid
            self.running_uid += 1
            # create data structures
            self.user_past_session_time.append([])  # session0_time, session1_time, session2_time ...
            self.user_past_session_dwell_time.append(
                [])  # session0_dwell_time, session1_dwell_time, session2_dwell_time ...
            self.user_past_tasks.append([])  # session0_tasks, session1_tasks, session2_tasks, ....
            self.user_past_session_stats.append([])  # (0)past_sessions_count, (1)total_tasks_count,
            # (2)total_sessions_time, (3)total_dwell_time
            self.user_current_session_stats.append([])  # (0)timestamp_of_previous_task_in_this_session,
            # (1)this_sessions_tasks_count,#  (2)this session_dwell_time,
            # (3)this_session_min_dwell_time, (4)this_session_start_time

            self.user_past_session_stats[user_id].append(0)
            self.user_past_session_stats[user_id].append(0)
            self.user_past_session_stats[user_id].append(0)
            self.user_past_session_stats[user_id].append(0)

            self.user_current_session_stats[user_id].append(-1)  # identify first task in session
            self.user_current_session_stats[user_id].append(0)
            self.user_current_session_stats[user_id].append(0)
            self.user_current_session_stats[user_id].append(-1)  # identify no min dwell time
            self.user_current_session_stats[user_id].append(0)

        else:  # user is known
            user_id = self.user_dict[user_sid]

        # update all auxilary structures

        last_seen = self.user_current_session_stats[user_id][clastseenidx]

        if (last_seen == -1):  # first task for this user
            self.user_current_session_stats[user_id][
                clastseenidx] = created_at  # this will be previous task time stamp for next task
            self.user_current_session_stats[user_id][ctaskidx] = 1  # first task
            self.user_current_session_stats[user_id][csstartidx] = created_at  # initialize session start time
            self.user_current_session_stats[user_id][cdwellidx] = 0  # zero dwell for first task in session
            self.user_current_session_stats[user_id][cmdwellidx] = -1  # no min dwell for first task in session

        else:
            delta = created_at - last_seen
            if ((delta.days == 0) and (delta.seconds <= 1800)):  # still in this session
                self.user_current_session_stats[user_id][ctaskidx] += 1  # increase this sessions tasks by one
                self.user_current_session_stats[user_id][cdwellidx] += (
                    created_at - last_seen).total_seconds()  # add to session dwell time
                min_dwell = self.user_current_session_stats[user_id][cmdwellidx]
                if (min_dwell == -1) or ((created_at - last_seen).total_seconds() < min_dwell):  # update min dwell
                    self.user_current_session_stats[user_id][cmdwellidx] = (created_at - last_seen).total_seconds()
                self.user_current_session_stats[user_id][
                    clastseenidx] = created_at  # this will be previous task ts for next task

            else:  # new session
                self.user_past_session_stats[user_id][pscountidx] += 1  # one more session just ended
                self.user_past_session_stats[user_id][ptasksidx] += self.user_current_session_stats[user_id][
                    ctaskidx]  # add task counts
                self.user_past_session_stats[user_id][pdwellidx] += self.user_current_session_stats[user_id][
                    cdwellidx]  # add dwell time
                past_session_time = 0
                if (self.user_current_session_stats[user_id][clastseenidx] != -1):  # one task in this session
                    past_session_time = (
                        self.user_current_session_stats[user_id][clastseenidx] - self.user_current_session_stats[user_id][
                            csstartidx]).total_seconds()
                self.user_past_session_stats[user_id][pstimeidx] += past_session_time  # add session duration

                # update running history
                self.user_past_session_time[user_id].append(past_session_time)
                self.user_past_session_dwell_time[user_id].append(
                    self.user_current_session_stats[user_id][cdwellidx] / self.user_current_session_stats[user_id][
                        ctaskidx])  # average!
                self.user_past_tasks[user_id].append(self.user_current_session_stats[user_id][ctaskidx])


                # update current session data
                self.user_current_session_stats[user_id][
                    clastseenidx] = created_at  # this will be previous task time stamp for next task
                self.user_current_session_stats[user_id][ctaskidx] = 1  # first task of this session
                self.user_current_session_stats[user_id][csstartidx] = created_at  # initialize session start time
                self.user_current_session_stats[user_id][cdwellidx] = 0  # zero dwell for first task in session
                self.user_current_session_stats[user_id][cmdwellidx] = -1  # no min dwell for first task in session

        # compute the features

        u_sessionCount = self.user_past_session_stats[user_id][pscountidx]
        s_minDwell = self.user_current_session_stats[user_id][cmdwellidx]
        s_avgDwell = self.user_current_session_stats[user_id][cdwellidx] / self.user_current_session_stats[user_id][
            ctaskidx]
        s_sessionTasks = self.user_current_session_stats[user_id][ctaskidx]
        s_sessionTime = (created_at - self.user_current_session_stats[user_id][csstartidx]).total_seconds()

        if (self.user_past_session_stats[user_id][pscountidx] == 0):  # no past sessions
            u_bHavePastSession = 0
            u_avgSessionTasks = 0
            u_medianSessionTasks = 0
            u_recentAvgSessionTasks = 0
            u_sessionTasksvsUserMedian = 0
            u_sessionTasksvsRecentMedian = 0
            u_avgSessionTime = 0
            u_sessionTimevsRecentAvg = 0
            u_sessionTimevsUserMedian = 0
            u_sessionAvgDwellvsUserAvg = 0
            u_sessionAvgDwellvsRecentAvg = 0
        else:
            u_bHavePastSession = 1
            u_avgSessionTasks = self.user_past_session_stats[user_id][ptasksidx] / \
                                self.user_past_session_stats[user_id][pscountidx]
            u_medianSessionTasks = self.median(self.user_past_tasks[user_id])
            len1 = np.clip(len(self.user_past_tasks[user_id]), 1, 10)
            u_recentAvgSessionTasks = self.avg(self.user_past_tasks[user_id][-len1:])
            u_sessionTasksvsUserMedian = self.user_current_session_stats[user_id][ctaskidx] - u_medianSessionTasks
            u_sessionTasksvsRecentMedian = self.user_current_session_stats[user_id][ctaskidx] - self.median(
                self.user_past_tasks[user_id][-len1:])
            u_avgSessionTime = self.avg(self.user_past_session_time[user_id])
            len2 = np.clip(len(self.user_past_session_time[user_id]), 1, 10)
            this_session_time = created_at - self.user_current_session_stats[user_id][csstartidx]
            u_sessionTimevsRecentAvg = this_session_time.total_seconds() - self.avg(
                self.user_past_session_time[user_id][-len2:])
            u_sessionTimevsUserMedian = this_session_time.total_seconds() - self.median(
                self.user_past_session_time[user_id])
            this_session_dwell_time = self.user_current_session_stats[user_id][cdwellidx] / \
                                      self.user_current_session_stats[user_id][ctaskidx]
            u_sessionAvgDwellvsUserAvg = this_session_dwell_time - self.avg(self.user_past_session_dwell_time[user_id])
            len3 = np.clip(len(self.user_past_session_dwell_time[user_id]), 1, 10)
            u_sessionAvgDwellvsRecentAvg = this_session_dwell_time - self.avg(
                self.user_past_session_dwell_time[user_id][-len3:])

        X_t = np.array([u_bHavePastSession,
                        u_sessionCount,
                        u_avgSessionTasks,
                        u_medianSessionTasks,
                        u_recentAvgSessionTasks,
                        u_sessionTasksvsUserMedian,
                        u_sessionTasksvsRecentMedian,
                        u_avgSessionTime,
                        u_sessionTimevsRecentAvg,
                        u_sessionTimevsUserMedian,
                        u_sessionAvgDwellvsUserAvg,
                        u_sessionAvgDwellvsRecentAvg,
                        s_minDwell,
                        s_avgDwell,
                        s_sessionTasks,
                        s_sessionTime])
        return X_t

    # Predicting
    def predicting(self, user_id, created_at):
        # logging.info("Starting prediction for User " + user_id)
        X_test = self.fe(user_id, created_at)
        y_predicted = self.clf.predict(X_test)
        if y_predicted == 1:
            self.y_leaving += 1
            #   print('User Leaving')
        else:
            self.y_staying += 1
            #  print('User Staying')
        return y_predicted

    def disratio(self):
        if self.y_leaving + self.y_staying == 0:
            return 0, 0
        return self.y_leaving / (self.y_leaving + self.y_staying), self.y_staying / (self.y_leaving + self.y_staying)



