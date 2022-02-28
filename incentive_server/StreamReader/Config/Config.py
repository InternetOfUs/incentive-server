from os.path import dirname
import os
__author__ = 'Daniel'
root_dir = dirname(dirname(dirname(dirname(__file__))))
logs_dir = root_dir + "/Logs/"
model_dir = root_dir + "/Model/"
predictor_dir = root_dir + "/src/Predictor/"


# : move this to proper yaml
class Config(object):
    conf = dict()

    # conf['clfFile'] ='/home/ise/Model/dismodel.pkl'
    conf['clfFile'] = model_dir + 'dismodel.pkl'

    # conf['strmLog'] = '/home/ise/Logs/streamer.log'
    conf['strmLog'] = logs_dir + 'streamer.log'

    # conf['predLog'] = '/home/ise/Logs/predictor.log'
    conf['predLog'] = logs_dir + 'predictor.log'

    # conf['dis_predLog'] = '/home/ise/Logs/dis_predictor.log'
    conf['dis_predLog'] = logs_dir + 'dis_predictor.log'

    conf['debug'] = False

    # conf['user'] = 'mysql_user'
    conf['user'] = 'root'

    # conf['password'] = 'mysql_password'
    conf['password'] = os.environ['MYSQL_PASSWORD']

    conf['host'] = os.environ['DB']

    conf['db'] = 'streamer'

    conf['duration_dist'] = predictor_dir + 'session_duration_for_distribution.csv'

    # conf['experiment_workflow_id'] = '11202'  # test workflow
    conf['experiment_workflow_id'] = '10582'  # galaxy zoo experiment workflow

    # conf['project_id_to_listen'] = 7800  # my test project
    conf['project_id_to_listen'] = 5733  # galaxy zoo
    conf['fake_Stream_url'] = 'http://127.0.0.1:5000/json'
    conf['UsersActivity_url'] = 'http://127.0.0.1:5000/UsersActivity'