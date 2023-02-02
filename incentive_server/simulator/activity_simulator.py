import json

__author__ = 'avisegal'
import random
import datetime
import requests
from time import sleep


class Simulator:

    #Input:

    def __init__(self):

        self.USERS_WANTED = 15000000  # "Input"


        fin_dwell = "dwell_time_per_task_dist_random.csv"
        fin_bwsession = "seconds_bw_sessions_dist_random.csv"
        fin_taskpersession = "users_dist.csv"
        fin_sessionsperuser = "sessions_per_user_dist_random.csv"


        self.users_behaviour_dist = {} #flag if user in in her normal_dist or dist_after_int_dist for

        self.user_interventions = {}   # int_id, last_int_session

        # Distribution of dwell time in session
        with open(fin_dwell) as f:
            self.baseline_dwell_dist = f.read().splitlines()
            self.baseline_dwell_dist = map(float, self.baseline_dwell_dist)


        # Distribution of # of sessions per user
        with open(fin_sessionsperuser) as f:
            self.baseline_sessions_per_user_dist = f.read().splitlines()
            self.baseline_sessions_per_user_dist = map(float, self.baseline_sessions_per_user_dist)

        # Distribution of tasks per session
        with open(fin_taskpersession) as f:
            self.baseline_tasks_per_sessions_dist = f.read().splitlines()
            self.baseline_tasks_per_sessions_dist = map(float, self.baseline_tasks_per_sessions_dist)
 #           self.baseline_tasks_per_sessions_dist = (50, 50, 50)

        # Distribution of distance between sessions
        with open(fin_bwsession) as f:
            self.baseline_seconds_bw_session_dist = f.read().splitlines()
            self.baseline_seconds_bw_session_dist = map(float, self.baseline_seconds_bw_session_dist)

        self.int1_dwell_dist = self.baseline_dwell_dist
        self.int1_sessions_per_user_dist = self.baseline_sessions_per_user_dist
#        self.int1_tasks_per_sessions_dist = [x * self.int_impact[0] for x in self.baseline_tasks_per_sessions_dist]
        self.int1_tasks_per_sessions_dist = self.baseline_tasks_per_sessions_dist
        self.int1_seconds_bw_session_dist = self.baseline_seconds_bw_session_dist

        self.int2_dwell_dist = self.baseline_dwell_dist
        self.int2_sessions_per_user_dist = self.baseline_sessions_per_user_dist
#        self.int2_tasks_per_sessions_dist = [x * self.int_impact[1] for x in self.baseline_tasks_per_sessions_dist]
        self.int2_tasks_per_sessions_dist = self.baseline_tasks_per_sessions_dist
        self.int2_seconds_bw_session_dist = self.baseline_seconds_bw_session_dist

        self.int3_dwell_dist = self.baseline_dwell_dist
        self.int3_sessions_per_user_dist = self.baseline_sessions_per_user_dist
#        self.int3_tasks_per_sessions_dist = [x * self.int_impact[2] for x in self.baseline_tasks_per_sessions_dist]
        self.int3_tasks_per_sessions_dist = self.baseline_tasks_per_sessions_dist
        self.int3_seconds_bw_session_dist = self.baseline_seconds_bw_session_dist


        self.users_per_min = 0.000004  # calculated from data


    def session_duration_in_range(self, inter, duration):
        if duration >= self.int_timing[inter-1][0] and duration <= self.int_timing[inter-1][1]:
            return True
        else:
            return False


    def check_int(self,user, session, tasks, session_start_time, session_duration):
        # decide if to administer intervention
        if user not in self.user_interventions:      # did not choose int for this user yet, choose what to give in due time
            int_id = random.randint(1,3)
            self.user_interventions[user] = (int_id, -1)

        int_id = self.user_interventions[user][0]
        int_session = self.user_interventions[user][1]
        task_factor = 1
        int_to_give = 0      # default - no intervention
        if (int_session != session) and self.session_duration_in_range(int_id, session_duration): # did not give intervention yet, and its time
            rnd = random.uniform(0,1)        # draw to decide if to give int in this session
            if rnd <=self.interventions_per_session:
                self.user_interventions[user] = (int_id, session)
                self.users_behaviour_dist[user] = int_id
                int_to_give = int_id
                task_factor = self.int_impact[int_id-1]
                #print (user, int_to_give, task_factor, session_duration, session)
        return int_to_give, task_factor


    def get_user_dist(self, user_id):
        if user_id not in self.users_behaviour_dist:
            self.users_behaviour_dist[user_id] = 0   # 0 is default dist; 1 is dist after intervention
        if self.users_behaviour_dist[user_id] == 0:
            return self.baseline_dwell_dist, self.baseline_sessions_per_user_dist, self.baseline_tasks_per_sessions_dist, self.baseline_seconds_bw_session_dist
        elif self.users_behaviour_dist[user_id] == 1:
            return self.int1_dwell_dist, self.int1_sessions_per_user_dist, self.int1_tasks_per_sessions_dist, self.int1_seconds_bw_session_dist
        elif self.users_behaviour_dist[user_id] == 2:
            return self.int2_dwell_dist, self.int2_sessions_per_user_dist, self.int2_tasks_per_sessions_dist, self.int2_seconds_bw_session_dist
        elif self.users_behaviour_dist[user_id] == 3:
            return self.int3_dwell_dist, self.int3_sessions_per_user_dist, self.int3_tasks_per_sessions_dist, self.int3_seconds_bw_session_dist

    def end_of_session_policy(self, user):
        self.users_behaviour_dist[user] = 0   # impact of intervention stops at session border

    def users_details(user_id):

        if user_id == 0 :

            return



    def simulate(self):
        url = 'http://127.0.0.1:8008/api/userActivity/'
        headers = {'Content-Type': 'application/json'}

        print ("Creating Simulated Data from field distributions...")

        simulator_pipeline = {}
        now = datetime.datetime.now()  # for realistic timestamps
        user_index = -1
        # Process:
        # Start at ti = 0
        time_stamp = 0
        print_counter = 0
        while user_index > -2:
            rnd = random.uniform(0,1)
        # Draw if new user joins system according to dist_new_user
        # If yes, allocate new user_id.
            if rnd <= self.users_per_min/60:
                user_index += 1
        #        print ("New User: " + str(user_index) + ", " + str(time_stamp))
                tasks_per_session = random.choice(self.baseline_tasks_per_sessions_dist)

                # Insert to Simulator_Pipeline: user_id, ti, session_id=0, # tasks for this user
                if time_stamp in simulator_pipeline:
                    current_pipe = simulator_pipeline[time_stamp]
                    current_pipe.append((user_index, 0, tasks_per_session, time_stamp))  #user, session, #tasks, session start time stamp
                    simulator_pipeline[time_stamp] = current_pipe
                else:
                    simulator_pipeline[time_stamp] = [(user_index, 0, tasks_per_session, time_stamp)] #user, session, #tasks, session start time stamp

        # Get out of Simulator_Pipeline all records with t=ti
            if time_stamp in simulator_pipeline:
                current_pipe = simulator_pipeline[time_stamp]
            else:
                time_stamp += 1
                continue

            # For each such user_i
            for user_sim in current_pipe:
                # Write to OUTPUT user_i, ti
                user = int(user_sim[0])
                session = int(user_sim[1])
                tasks = int(user_sim[2])
                session_start_time = int(user_sim[3])
                rand = random.uniform(0,1)
                discussion = 0
                post = 0
                discussion_id = 0
                if rand <= 0.2:
                    discussion = 1
                if rand >= 0.7:
                    post = 1


                session_duration = time_stamp - session_start_time

                # todo: you mast change the discussion_id to unic number in case of post!
                if (discussion == 1 or post == 1) and user > 0:
                    print_counter += 1
                    data = {'user_id': str(tasks), 'app_id': str(1), 'discussion': str(discussion), 'post': str(post),
                            'discussion_id': str(user)}
                    r = requests.post(url, data=json.dumps(data), headers=headers)
                    print (data)
                    sleep(1)
                    # hello(str(user), str(now + datetime.timedelta(seconds=time_stamp)))
                dwell_dist, session_dist, task_dist, bw_dist = self.get_user_dist(user)

                if int(tasks) > 1: # more tasks for this user and session
                    # Decide dwell_time from distribution
                    dwell_time = random.choice(dwell_dist)
                    new_time = time_stamp + int(float(dwell_time))
                    # Insert to Simulator_Pipeline: user_i, ti+dwell_time
                    if new_time in simulator_pipeline:
                        npipe = simulator_pipeline[new_time]
                        npipe.append((user, session, int(tasks)-1, session_start_time))
                        simulator_pipeline[new_time] = npipe
                    else:
                        simulator_pipeline[new_time]=[(user, session, int(tasks)-1, session_start_time)]
                # If session terminates:
                else: # session ends

                    self.end_of_session_policy(user)     # need to update dist for next session of this user if any
                    # Draw if there is another session using dist_num_sessions
                    sessions_for_user = random.choice(session_dist)
                    # If not, continue to next user_i
                    if int(session) + 1 >= int(sessions_for_user):
                        continue
                    # If yes:
                    else:
                        # draw gap_untill_next_session using dist_sessions_gap
                        gap = random.choice(bw_dist)

                        # Add user_i, ti+draw dwell_untill_next_session, session_id+1 to Simulator_Pipeline
                        new_time = time_stamp + int(float(gap))
                        # Insert to Simulator_Pipeline: user_i, session + 1, ti+dwell_time, tasks_for_new_sessions
                        tasks_for_new_session=random.choice(task_dist)

                        if new_time in simulator_pipeline:
                            npipe = simulator_pipeline[new_time]

                            npipe.append((user, session+1, tasks_for_new_session, new_time))
                            simulator_pipeline[new_time] = npipe
                        else:
                            simulator_pipeline[new_time]=[(user, session+1, tasks_for_new_session, new_time)]

            simulator_pipeline.pop(time_stamp, None) # finished with this timestamp
            # ti=ti+1
            time_stamp +=1
        # note: leaving some events in pipeline for now once last user created. Simulating Right Censoring

sm = Simulator()
sm.simulate()

