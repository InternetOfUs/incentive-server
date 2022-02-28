from os.path import dirname
import os
__author__ = 'eran'
root_dir = dirname(dirname(dirname(__file__)))
logs_dir = root_dir + "/Logs/"
model_dir = root_dir + "/Model/"
predictor_dir = root_dir + "/src/Predictor/"


# todo: move this to proper yaml
class Config(object):
    conf = dict()
    conf['last_update'] = None
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
    conf['password'] = os.getenv('MYSQL_PASSWORD')

    conf['host'] = os.getenv('DB')

    conf['db'] = 'streamer'

    conf['activity_stream_db'] = 'lassi'

    conf['duration_dist'] = predictor_dir + 'session_duration_for_distribution.csv'

    conf['production'] = False

