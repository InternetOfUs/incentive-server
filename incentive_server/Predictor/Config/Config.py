from os.path import dirname
import  os
__author__ = 'Daniel'
root_dir = dirname(dirname(dirname(dirname(__file__))))
logs_dir = root_dir + "/Logs/"
model_dir = root_dir + "/Model/"
predictor_dir = root_dir + "/src/Predictor/"


# todo: move this to proper yaml
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

    conf['emphasis_learning'] = "A computer is learning to classify galaxies. It needs your classifications to get better!"

    conf['emphasis_automation'] = "We are using computer models to automatically classify easy galaxies. We need you to classify the hard ones!"

    conf['emphasis_accuracy'] = "A computer has already classified these galaxies but it could be wrong. We need your help to make more accurate classifications."

    conf['emphasis_efficiency'] = "We are combining human and automatic computer classifications. By classifying these galaxies you are helping us to get correct answers much more efficiently."

    conf['interventions_id_to_text'] = {
        1: conf['emphasis_learning'],
        2: conf['emphasis_automation'],
        3: conf['emphasis_accuracy'],
        4: conf['emphasis_efficiency']
    }

    # conf['experiment_workflow_id'] = '11202'  # test workflow
    conf['experiment_workflow_id'] = '10582'  # galaxy zoo experiment workflow

    # conf['production'] = False
    conf['production'] = True

