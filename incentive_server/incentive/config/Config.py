from os.path import dirname
import os
__author__ = 'Daniel'
root_dir = dirname(dirname(dirname(dirname(__file__))))



# todo: move this to proper yaml
class Config(object):

    def __init__(self):
        self.issuer = 'mT7hgXVkQMShRxRWIusVSg'
        self.relations_badges = {
            'badges': {
                "friendly": 10,
                "popular": 20,
                "famous": 40
            },
            'badges_id': {
                "friendly": 'RTR8KkZbRLO45QTHM6WUUA',
                "popular": 'wV30wX0VTXm2PVPVcxMr5w',
                "famous": 'hpqAdI7hQf2maQ13AW1jXA'
            },
            }
        self.touch_badges = {
            'badges': {
                "Hero": 10,
                "Champion": 30,
                "Guro": 50
            },
            'badges_id': {
                "Hero": 'DqQzjMKWQNipb1o9Fbaqjw',
                "Champion": 'yPBbuTgFRQuD3JzsQ5bG-w',
                "Guro": 'Vc8ywfpPSqynCDFfig3GhQ'
            },
            }
        self.questions_x = 5
        self.answers_x = 5
        self.good_answers_x = 5
        self.questions = {
            'badges': {
                "1": 'First question',
                self.questions_x: 'Curious level 1',
                2*self.questions_x: 'Curious level 2'
            },
            'badges_id': {
                "First question": 'dKBzDAIXSKeCUfmOaRsjmA',
                "Curious level 1": 'BkegdiFVRi2xqLnvlM8A9A',
                "Curious level 2": 'whp4Ukz9S--sI1zmakznjg'
            },
            }
        self.answers = {
            'badges': {
                "1": 'First answer',
                self.answers_x: 'Helper level 1',
                2*self.answers_x: 'Helper level 2'
            },
            'badges_id': {
                "First answer": 'dCOeYJzLTc-AvnpWDWTaNg',
                "Helper level 1": '9dw_UfwPRxW3rBqXT3zT9A',
                "Helper level 2": 'QHqVe9QeRr-UJTU47D4Ssw'
            },
            }
        self.good_answers = {
            'badges': {
                "1": 'First Good Answer',
                self.good_answers_x: 'Good Answers level 1',
                2 * self.good_answers_x: 'Good Answers level 2'
            },
            'badges_id': {
                "First Good Answer": '9G6pv1jGSPyDlOHopPA0Bw',
                "Good Answers level 1": 'uV38wVc6QAacXQ94b-ogGQ',
                "Good Answers level 2": 'SfYh9RcSRy6YoOsV8cP8rQ'
            },
        }
        self.conf = dict()

    def get_config(self):
        conf = self.conf
        conf['url_badgr'] = os.getenv('BADGR_DOMAIN')
        conf['api_key'] = os.getenv('COMP_AUTH_KEY')
        conf['url_get_badges'] = f'v2/issuers/{self.issuer}/badgeclasses'
        conf['url_badge_user'] = 'v1/user/profile'
        conf['url_badgeClass_assertions'] = 'v2/badgeclasses/%s/assertions'
        conf['url_issue_badge'] = 'v2/badgeclasses/%s/assertions'
        conf['badgr_token'] = os.getenv('Badger_TOKEN')
        conf['url_all_assertions'] =f'v2/issuers/{self.issuer}/assertions'
        conf['get_badge_class'] = 'v2/badgeclasses/%s'
        conf_prod = conf.copy()
        conf_beta = conf.copy()

        if os.getenv('ENVIRONMENT') == 'beta':  # beta version
            conf_beta['url_badgr'] = 'https://wenet.u-hopper.com/beta/badgr/'

        if os.getenv('ENVIRONMENT') == 'prod_test':  # prod testing
            conf_prod['url_badgr'] = 'https://internetofus.u-hopper. /prod/badgr/'

        conf['url_wenet_post_incentive'] ='https://wenet.u-hopper.com/dev/interaction_protocol_engine/incentives'
        # conf['url_wenet_post_incentive'] ='https://ardid.iiia.csic.es/wenet/interaction-protocol-engine/incentives'
        conf_beta['url_wenet_post_incentive'] ='https://wenet.u-hopper.com/beta/interaction_protocol_engine/incentives'
        conf_prod['url_wenet_post_incentive'] ='https://internetofus.u-hopper.com/prod/interaction_protocol_engine/incentives'

        conf['url_wenet_get_user'] = 'https://wenet.u-hopper.com/dev/profile_manager/profiles/%s'
        # conf['url_wenet_get_user'] = 'https://ardid.iiia.csic.es/wenet/profile-manager/profiles/%s'
        conf_beta['url_wenet_get_user'] = 'https://wenet.u-hopper.com/beta/profile_manager/profiles/%s'
        conf_prod['url_wenet_get_user'] = 'https://internetofus.u-hopper.com/prod/profile_manager/profiles/%s'

        conf['url_wenet_get_app_open_tasks'] = 'https://wenet.u-hopper.com/dev/task_manager/tasks?appId=%s&hasCloseTs=false&limit=1000000'
        # conf['url_wenet_get_app_open_tasks'] = 'https://ardid.iiia.csic.es/wenet/task-manager/tasks?appId=%s&hasCloseTs=false&limit=1000000'
        conf_beta['url_wenet_get_app_open_tasks'] = 'https://wenet.u-hopper.com/beta/task_manager/tasks?appId=%s&hasCloseTs=false&limit=1000000'
        conf_prod['url_wenet_get_app_open_tasks'] = 'https://internetofus.u-hopper.com/prod/task_manager/tasks?appId=%s&hasCloseTs=false&limit=1000000'

        conf['get_actions_on_task_app_label'] = 'https://wenet.u-hopper.com/dev/task_manager/taskTransactions?appId=%s&limit=%s&label=%s&actioneerId=%s'
        # conf['get_actions_on_task_app_label'] = 'https://ardid.iiia.csic.es/wenet/task-manager/taskTransactions?appId=%s&limit=%s&label=%s&actioneerId=%s'
        conf_beta['get_actions_on_task_app_label'] = 'https://wenet.u-hopper.com/beta/task_manager/taskTransactions?appId=%s&limit=%s&label=%s&actioneerId=%s'
        conf_prod['get_actions_on_task_app_label'] = 'https://internetofus.u-hopper.com/prod/task_manager/taskTransactions?appId=%s&limit=%s&label=%s&actioneerId=%s'

        # conf['get_actions_on_task_app_label'] = 'https://wenet.u-hopper.com/dev/task_manager/taskTransactions?appId=%s&limit=1000&actioneerId=%s'
        # conf_prod['get_actions_on_task_app_label'] = 'https://internetofus.u-hopper.com/prod/task_manager/taskTransactions?appId=%s&limit=1000&actioneerId=%s'

        conf['wenet_get_users_by_app'] = 'https://wenet.u-hopper.com/dev/service/app/%s/users'
        conf_beta['wenet_get_users_by_app'] = 'https://wenet.u-hopper.com/beta/service/app/%s/users'
        conf_prod['wenet_get_users_by_app'] = 'https://internetofus.u-hopper.com/prod/service/app/%s/users'

        
        if os.environ.get('ENVIRONMENT') == 'beta':
            return conf_beta
        if os.environ.get('ENVIRONMENT') in ['prod', 'prod_test']:
            return conf_prod
        if os.environ.get('ENVIRONMENT') == 'test':
            conf_prod['url_wenet_post_incentive'] = 'http://localhost:8000/test_post/'
            return conf_prod
        return conf

    def get_touch_badges(self):
        return self.touch_badges

    def get_relations_badges(self):
        return self.relations_badges

    def get_questions_badges(self):
        return self.questions

    def get_answers_badges(self):
        return self.answers

    def get_good_answers_badges(self):
        return self.good_answers

