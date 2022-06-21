from __future__ import division
# from _typeshed import NoneType
import ast
import traceback
import requests
# import MySQLdb
import pymysql

from random import SystemRandom
import string

import json
from json import JSONEncoder
import datetime
from contextlib import closing

# from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http.response import HttpResponseBadRequest
from django.http import HttpResponse, StreamingHttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition
from django.views.decorators.cache import never_cache

# from rest_framework.decorators import detail_route
from rest_framework.decorators import action

from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework import viewsets
from rest_framework.authtoken.models import Token

# from permissions import IsOwnerOrReadOnly
from .forms import getUserForm
from .models import models
from .models import Document
from .models import Complaint, LocationEvent, SocialRelations, \
    TouchEvents, TimeDiaries
from .forms import DocumentForm
from .runner import getTheBestForTheUser
from .serializers import *
from .tests import check_user, check_app, check_community, check_inc_status
from .badges.Badges import get_all_users_badges, get_user_email_temp, get_user_email,\
     get_badge_details_from_response,get_all_badges_app, handle_task_status, issue_badge_if_not_exists, get_all_badges
from .badges.BadgeClassValidators import check_image_url, getBadgeClass, putBadgeClass, revokeBadgeClassAssertions
from .messages.Messages import start, is_post_incentive_message_valid,\
     get_incentive_message_valid, put_incentive_message,get_incentive_message_detial,all_issued
from os.path import dirname
from django.core.cache import cache
import sys
src_dir = (dirname(dirname(__file__)))
sys.path.append(src_dir)

from Config.Config import Config
from utils.utils import mysql_connect as _mysql_connect, get_stream_latest_id
from .helper import insert_user_if_not_exist, respond_json, api_call


from incentive.config.Config import Config as Conf

Conf = Conf()
config_list = Conf.get_config()

config = Config.conf


def test_func(request):
    email, cohort = insert_user_if_not_exist(1, 'x')
    return HttpResponse(email, cohort)


class TestPost(APIView):
    def post(self, request, format=None):
        return HttpResponse('OK test')


# @csrf_exempt
# @never_cache
# def dashStream(request):
#     # todo i think this is never used, so delete
#     print("I WAS HERE!!!!!!")
#     conn = django_mysql_connect()
#     datetimeO = str(request.REQUEST.dicts[0][u'date'])
#     cursor = conn.cursor()
#     try:
#         data = []
#         cursor.execute("SELECT user_id,created_at FROM stream WHERE created_at>=%s" % (datetimeO))
#
#         rows = cursor.fetchall()
#         for row in rows:
#             data.insert(0, '{"user_id":"' + row[0] + '","created_at":"' + str(row[1]) + '"}')
#
#
#     except MySQLdb.Error as e:
#         conn.rollback()
#     conn.close()
#     return HttpResponse(json.dumps(data))


# def getSecret():
#     # todo i think this is never used, so delete
#     print("I WAS HERE!!!!!!")
#     conn = django_mysql_connect()
#     cursor = conn.cursor()
#     try:
#
#         cursor.execute("SELECT * FROM secret ")
#
#         row = cursor.fetchone()
#     except MySQLdb.Error as e:
#         conn.rollback()
#     conn.close()
#     badgr_token = row[1]
#     badgr_domain = row[0]
#     return badgr_token , badgr_domain

def home(request):
    return render(request, "signups.html", locals())


def thankyou(request):
    return render(request, "thankyou.html", locals())


def debug_messages(request):
    start()
    return HttpResponse(status=200)

@csrf_exempt
@never_cache
def dash(request):
    return render(request, "dash/pages/dash.html", locals(), )
def badgesdash(request):
    return render(request, "badgesdash/pages/dash.html", locals(), )

def wiki(request):
    # return render_to_response("Wiki.html", locals(), context_instance=RequestContext(request))
    return HttpResponseRedirect('http://swagger.u-hopper.com/?url=https://bitbucket.org/wenet/wenet-components-documentation/raw/master/sources/wenet-incentive-server-api.json')

def aboutus(request):
    return render(request, "aboutus.html", locals())




class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class IncetiveViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Incentive.objects.all()
    serializer_class = IncentiveSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly)

    @action(detail=False, methods=['GET'], name='Get Highlight')
    def highlight(self, request, *args, **kwargs):
        # incentive = self.get_object()
        # return Response(incentive.highlighted)
        queryset = models.Highlight.objects.all()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # def perform_create(self, serializer):
    #         serializer.save()
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


# class IncentiveHighlight(generics.GenericAPIView):
#     queryset = Incentive.objects.all()
#     renderer_classes = (renderers.StaticHTMLRenderer,)
#
#     def get(self, request, *args, **kwargs):
#         incentive = self.get_object()
#         return Response(incentive.highlighted)

class IncentiveView(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    queryset = Incentive.objects.all()
    serializer_class = IncentiveSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly)

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [incentive.status for incentive in Incentive.objects.all()]
        return Response(usernames)


@csrf_exempt
@never_cache
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        username = data[u'username']
        password = data[u'password']
        user = None
        try:
            user = User.objects.get(username=username)
        except:
            pass
        if user is not None and user.check_password(password):
            token = Token.objects.get_or_create(user=user)
            return JSONResponse("{'Token':'" + token[0].key + "'}")
    return JSONResponse("{'Token':'0'}")


@csrf_exempt
@never_cache
def incetive_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        # incentive = Incentive.objects.all()
        staa = request.GET
        tmp = dict(staa.lists())
        token = tmp[u'Token']
        t = str(token[0])
        testToken = None
        try:
            testToken = Token.objects.get(key=token[0])
        except:
            testToken = None
        incentive = None
        if (testToken is not None):
            for key in tmp:
                if key == 'tagID':
                    tags = Tag.objects.filter(tagID=tmp[key][0])
                    incentive = Incentive.objects.filter(tags=tags)
                if key == 'status':
                    incentive = Incentive.objects.filter(status=tmp[key])
                if key == 'groupIncentive':
                    incentive = Incentive.objects.filter(groupIncentive=tmp[key])
                if key == 'typeID':
                    incentive = Incentive.objects.filter(typeID=tmp[key][0])
                if key == 'schemeID':
                    incentive = Incentive.objects.filter(schemeID=tmp[key][0])
        if incentive is None:
            return JSONResponse("{err:Wrong Argument}", status=404)
        serializer = IncentiveSerializer(incentive, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = IncentiveSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)


@csrf_exempt
@never_cache
def incetive_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        incentive = Incentive.objects.get(pk=pk)
    except Incentive.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = IncentiveSerializer(incentive)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = IncentiveSerializer(incentive, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        incentive.delete()
        return HttpResponse(status=204)


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'incentive': reverse('incentive-list', request=request, format=format),
    })


# @api_view()
# def xml(request):
#     o="Fail-PATH: "
#     o+=os.path.dirname(__file__)
#     o+='/Text.xml'
#     fileName=os.path.dirname(__file__)+'/Test.xml'
#     if os.path.isfile(fileName):
#         with open(fileName,'r') as f:
#            str = f.read().replace('\n', '')
#         o= xmltodict.parse(str)
#     return Response(json.dumps(o))


@api_view()
def about(request):
    return Response({"Created_By": "BGU Applied AI"})


# @api_view()
# def incentiveTest(request):
#     """
#     Convert given text to uppercase
#     (as a plain argument, or from a textfile's URL)
#     Returns an indented JSON structure
#     """
#
#     # Store HTTP GET arguments
#     plain_text = request.GET.get('s', default=None)
#     textfile_url = request.GET.get('URL', default=None)
#     io = StringIO()
#     if plain_text is None:
#         return Response(json.dumps(
#             {'incentive': "Send Email"
#              },
#             indent=4))
#
#     # Execute WebService specific task
#     # here, converting a string to upper-casing
#     if plain_text is not None:
#         return Response(json.dumps(
#             {'input': plain_text,
#              'result': plain_text.upper()
#              },
#             indent=4))
#
#     elif textfile_url is not None:
#         textfile = urllib2.urlopen(textfile_url).read()
#         return Response(json.dumps(
#             {'input': textfile,
#              'output': '\n'.join([line.upper() for line in textfile.split('\n')])
#              },
#             indent=4))


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'], owner=request.user)
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('incentive.views.list'))
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = None
    if request.user.is_active:
        documents = Document.objects.filter(owner=request.user)

    # Render list page with the documents and the form
    return render(request, 'list.html', locals())



@csrf_exempt
@never_cache
def getUserID(request):
    if request.method == 'POST':
        form = getUserForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = str(form.data[u'userID'])
            date = str(form.data[u'created_at'])
            BestIncentive = getTheBestForTheUser(request, newdoc, date).content
            # Redirect to the document list after POST
            # Render list page with the documents and the form
            return HttpResponse(json.dumps(BestIncentive))
            # return render_to_response('GetUser.html', locals(), context_instance=RequestContext(request))
        else:
            return HttpResponse(json.dumps({'error': "form is not valid"}))
    else:
        try:
            form = getUserForm()  # A empty, unbound form
        except Exception as e:
            d = {'error': str(e),
                 'trace:': traceback.format_exc(),
                 'config': config}
            return HttpResponse(json.dumps(d))

        return render(request, 'GetUser.html', locals())


def userProfile(request):
    # Load documents for the list page
    incentivesList = []
    incentives = None
    if request.user.is_active:
        incentives = Incentive.objects.filter(owner=request.user)
        for incentive in incentives:
            incentivesList.append(str(incentive.schemeID) + ":" + incentive.schemeName)
        documents = Document.objects.filter(owner=request.user)
    # user=User.objects.get(username=request.user)

    return render(request,
        'profilePage.html', locals(),

    )


# class Config(object):
#     conf = dict()
#     # conf['clfFile'] ='/home/ise/Model/dismodel.pkl'
#     # conf['clfFile'] ='/Users/avisegal/models/dtew/dismodel.pkl'
#     conf['clfFile'] = '/home/eran/Documents/Lassi/src/Algorithem/Model/dismodel.pkl'
#
#     # conf['strmLog'] = '/home/ise/Logs/streamer.log'
#     conf['strmLog'] = '/home/eran/Documents/Logs/streamer.log'
#
#     # conf['predLog'] = '/home/ise/Logs/predictor.log'
#     conf['predLog'] = '/home/eran/Documents/Logs/predictor.log'
#
#     # conf['dis_predLog'] = '/home/ise/Logs/dis_predictor.log'
#     conf['dis_predLog'] = '/home/eran/Documents/Logs/dis_predictor.log'
#
#     conf['debug'] = False
#
#     conf['user'] = 'root'
#
#     conf['password'] = '9670'
#
#     conf['host'] = 'localhost'
#
#     conf['db'] = 'streamer'
#
#
# cnf = Config().conf


@condition(etag_func=None)
@csrf_exempt
@never_cache
def stream_response(request):
    resp = StreamingHttpResponse(stream_response_generator())
    return resp


@csrf_exempt
@never_cache
def stream_response_generator2():
    for x in range(1, 11):
        yield x
        yield '\n'


@csrf_exempt
@never_cache
def stream_response_generator():
    try:
        conn = django_mysql_connect()
        conn.autocommit(True)
        cursor = conn.cursor()
    except:
        return
    local_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    while True:
        cursor.execute(
            """SELECT id,user_id,created_at,intervention_id
            FROM stream
            WHERE (local_time>"%s") and
            intervention_id is Not NULL""" % local_time)
        rows = cursor.fetchall()
        if len(rows) == 0:
            continue
        local_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        for row in rows:
            if (row is None) or (len(row) < 4):
                print (row)
                continue
            id = row[0]
            user_id = row[1]
            created_at = row[2]
            intervention_id = row[3]
            jsonToStream = JSONEncoder().encode({
                "id": str(id),
                "user_id": str(user_id),
                "created_at": str(created_at),
                "intervention_id": str(intervention_id)
            })
            if created_at.strftime('%Y-%m-%d %H:%M:%S') > local_time:
                local_time = (created_at + datetime.timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
            try:
                yield jsonToStream
                yield "\n"
            except:
                continue


# @csrf_exempt
# @never_cache
# def ask_by_date(request):
#     try:
#         return _ask_by_date(request)
#     except Exception as e:
#         return JSONResponse({
#             'error:': str(e),
#             'traceback': traceback.format_exc(),
#             'config': config,
#         })


# def _ask_by_date(request):
#     print("ask_by_date was requested")
#     conn = django_mysql_connect()
#
#     # conn.autocommit(True)
#     cursor = conn.cursor()
#
#     local_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
#     # search = True
#     response = []
#     # while search:
#     cursor.execute(
#         """SELECT id,user_id,created_at,intervention_id,preconfigured_id,cohort_id,algo_info,country_name
#         FROM stream
#         WHERE (local_time>"%s") and
#         (user_id!="Not Logged In") and
#         intervention_id is Not NULL""" % local_time)
#
#     rows = cursor.fetchall()
#     # if len(rows) == 0:
#     #     continue
#     # search = False
#     for row in rows:
#         # if (row is None) or (len(row) < 8):
#             # continue
#         _id = row[0]
#         user_id = row[1]
#         created_at = row[2]
#         intervention_id = row[3]
#         preconfigured_id = row[4]
#         cohort_id = row[5]
#         algo_info = row[6]
#         country_name = row[7]
#         # jsonToSend = JSONEncoder().encode({
#         data = {
#             "id": _id,
#             "user_id": str(user_id),
#             "created_at": str(created_at),
#             "intervention_id": str(intervention_id),
#             "preconfigured_id": str(precfratheronfigured_id),
#             "cohort_id": str(cohort_id),
#             "algo_info": str(algo_info),
#             "country_name": str(country_name)
#         }
#         response.append(data)
#         # response.append('\n')
#     # return JSONResponse(json.dumps(response))
#     return JSONResponse(response)

latest_id_on_dashboard_session = None

last_update = None



@csrf_exempt
@never_cache
def mark_latest_id(request):
    conn = django_mysql_connect()
    conn.autocommit(True)
    cursor = conn.cursor()
    latest_id = get_stream_latest_id(cursor)
    global latest_id_on_dashboard_session
    latest_id_on_dashboard_session = latest_id
    return HttpResponse(latest_id)


def django_mysql_connect():
    # this is done because the regular user 'root' is already in use by django
    try:
        conn = _mysql_connect(**config)
    except pymysql.OperationalError:  # user refused access
        # todo move this to config
        conn = _mysql_connect(host=os.environ['DB'], user='root', password=os.environ['MYSQL_PASSWORD'], db='streamer')
    return conn


@csrf_exempt
@never_cache
def get_new_classifications_test(request):
    try:
        return _get_new_classifications_test(request)
    except Exception as e:
        return JSONResponse(
            {'error': e,
             'trace': traceback.format_exc()}
        )


@csrf_exempt
@never_cache
def get_new_classifications(request):
    try:
        return _get_new_classifications(request)
    except Exception as e:
        return JSONResponse(
            {'error': e,
             'trace': traceback.format_exc()}
        )


def _get_new_classifications_test(request):
    conn = django_mysql_connect()
    conn.autocommit(True)
    cursor = conn.cursor()
    response = []
    cursor.execute(
        """SELECT id,user_id,created_at,intervention_id,preconfigured_id,cohort_id,algo_info,country_name
        FROM stream
        WHERE (id>"%s")""" % 95)
    rows = cursor.fetchall()
    id_set = set()
    for row in rows:
        _id = row[0]
        id_set.add(_id)

        json_to_send = create_classification_json(row)
        response.append(json_to_send)
        response.append('\n')

    response.append("*\n*\n*\n")

    for row in rows:
        _id = row[0]
        id_set.add(_id)

        json_to_send = str(create_classification_json_test(row))
        response.append(json_to_send)
        response.append('\n')

    return HttpResponse(response)


def _get_new_classifications(request):
    global latest_id_on_dashboard_session
    if latest_id_on_dashboard_session is None:
        return HttpResponse([])

    conn = django_mysql_connect()
    cursor = conn.cursor()
    response = []
    cursor.execute(
        """SELECT id,user_id,created_at,intervention_id,preconfigured_id,cohort_id,algo_info,country_name
        FROM stream
        WHERE (id>"%s" AND preconfigured_id IS NOT NULL)""" % latest_id_on_dashboard_session)
    rows = cursor.fetchall()

    # preconfigured_id IS NOT NULL because we want it only after the predictor is done with it

    id_set = set()
    for row in rows:
        _id = row[0]
        id_set.add(_id)

        json_to_send = create_classification_json(row)
        response.append(json_to_send)
        response.append('\n')

    if id_set:
        latest_id_found = max(id_set)

        latest_id_on_dashboard_session = latest_id_found

    return HttpResponse(response)


def create_classification_dict_test(row):
    _id = row[0]
    user_id = row[1]
    created_at = row[2]
    intervention_id = row[3]
    preconfigured_id = row[4]
    cohort_id = row[5]
    algo_info = row[6]
    country_name = row[7]
    return {
        "id": _id,
        "user_id": str(user_id),
        "created_at": str(created_at),
        "intervention_id": str(intervention_id),
        "preconfigured_id": str(preconfigured_id),
        "cohort_id": str(cohort_id),
        "algo_info": str(algo_info),
        "country_name": str(country_name)
    }


def create_classification_json_test(row):
    _id = row[0]
    user_id = row[1]
    created_at = row[2]
    intervention_id = row[3]
    preconfigured_id = row[4]
    cohort_id = row[5]
    algo_info = row[6]
    country_name = row[7]
    return {
        "id": _id,
        "user_id": str(user_id),
        "created_at": str(created_at),
        "intervention_id": str(intervention_id),
        "preconfigured_id": str(preconfigured_id),
        "cohort_id": str(cohort_id),
        "algo_info": str(algo_info),
        "country_name": str(country_name)
    }


def create_classification_json(row):
    _id = row[0]
    user_id = row[1]
    created_at = row[2]
    intervention_id = row[3]
    preconfigured_id = row[4]
    cohort_id = row[5]
    algo_info = row[6]
    country_name = row[7]
    jsonToSend = JSONEncoder().encode({
        "id": _id,
        "user_id": str(user_id),
        "created_at": str(created_at),
        "intervention_id": str(intervention_id),
        "preconfigured_id": str(preconfigured_id),
        "cohort_id": str(cohort_id),
        "algo_info": str(algo_info),
        "country_name": str(country_name)
    })
    return jsonToSend


@csrf_exempt
@never_cache
def GiveRatio(request):
    print ("Give Ratio Requested")
    num_of_leaving = 0
    num_of_staying = 0
    leaving_fracture = 0  # "1.0"/"1.0"+"0.0"
    staying_fracture = 0  # "0.0"/"1.0"+"0.0"
    try:
        conn = django_mysql_connect()
        conn.autocommit(True)
        cursor = conn.cursor()

        cursor.execute('SELECT  count(*) AS count  FROM stream WHERE (algo_info >  0.5)')  # leaving
        rows = cursor.fetchall()
        if len(rows) == 0:
            return JSONResponse('{"DB":"Unable to read db"}')
        for row in rows:
            try:
                num_of_leaving = row[0]
            except:
                return JSONResponse('{"DB":"Unable to read db"}')

        cursor.execute('SELECT  count(*) AS count  FROM stream WHERE (algo_info <= 0.5)')  # staying
        rows = cursor.fetchall()
        if len(rows) == 0:
            return JSONResponse('{"DB":"Unable to read db"}')
        for row in rows:
            try:
                num_of_staying = row[0]
            except:
                return JSONResponse('{"DB":"Unable to read db"}')
        if num_of_leaving > 0 or num_of_staying > 0:
            leaving_fracture = num_of_leaving / (num_of_leaving + num_of_staying)
            staying_fracture = num_of_staying / (num_of_leaving + num_of_staying)

        ratio = ["{\"l\":" + str(leaving_fracture) + ",\"s\":" + str(staying_fracture) + "}"]
        jsonIncentive = json.dumps(ratio)
        print (jsonIncentive)
        return JSONResponse(jsonIncentive)
    except:
        return JSONResponse('{"DB":"Error"}')


def sql(query, params):
    # connect
    conn = django_mysql_connect()
    with closing(conn.cursor()) as cursor:
        try:
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except:
            print (sys.exc_info())
            conn.rollback()
            conn.close()
            return False


@csrf_exempt
@never_cache
def receive_event(request):
    try:
        received_json_data = json.loads(request.body)
        source = received_json_data['source']
        event_type = received_json_data['event_type']
        timestamp = received_json_data['timestamp']
        user_id = received_json_data['user_id']
        experiment_name = received_json_data['experiment_name']
        project = received_json_data['project']
        if 'additional_info' in received_json_data:
            additional_info = received_json_data['additional_info']
        else:
            additional_info = None
        if sql(
                """INSERT INTO events (source,event_type,timestamp,user_id,experiment_name,project,additional_info) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (source, event_type, timestamp, user_id, experiment_name, project, additional_info)):
            return HttpResponse("OK")
        else:
            return HttpResponseBadRequest("Unable to save event.")
    except:
        print (sys.exc_info())
        return HttpResponseBadRequest("Malformed Data!")


class DisableIncentives(APIView):
    def post(self, request, **kwargs):
        if b'reason' not in request.body:
            return HttpResponseBadRequest("You Must supply reason ")
        if check_inc_status:

            body_unicode = request.body.decode('utf-8')
            received_json_data = json.loads(body_unicode)
            reason = received_json_data['reason']
            data = {
                  "message_id": 145,
                  "message": "successful operation"
            }
            return JsonResponse(data)
        else:
            return HttpResponseBadRequest("The server is already disabled", status = 403)


class UsersCohortsViewSet(viewsets.ModelViewSet):
    queryset = UsersCohorts.objects.all()
    serializer_class = UsersCohortsSerializer


class WeNetUsersViewSet(viewsets.ModelViewSet):
    queryset = WeNetUsers.objects.all()
    serializer_class = WeNetUsersSerializer


#class IncentiveAppViewSet(viewsets.ModelViewSet):
#    queryset = IncentiveApp.objects.all()
#    serializer_class = IncentiveAppSerializer
#
#    def create(self, request):
#        serializer = IncentiveAppSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            json_data = json.loads(json.dumps(request.data))
#            return JsonResponse(json_data, safe=False)


class WeNetAppsViewSet(viewsets.ModelViewSet):
    queryset = WeNetApps.objects.all()
    serializer_class = WeNetAppsSerializer

    def create(self, request):
        serializer = WeNetAppsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            json_data = json.loads(json.dumps(request.data))
            return JsonResponse(json_data, safe=False)


class TaskStatusViewSet(viewsets.ModelViewSet):
    queryset = TaskStatus.objects.all()
    serializer_class = TaskStatusSerializer

    def create(self, request):
        if request.data.get('label') in ['AnsweredQuestionMessage', 'QuestionToAnswerMessage']:
            return JsonResponse({"message": "labels 'AnsweredQuestionMessage' and 'QuestionToAnswerMessage' are not to be inserted into task_status table",
                                 "status_code": 200})
        serializer = TaskStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            json_data = json.loads(json.dumps(request.data))
            response = handle_task_status(json_data)
            if type(response) is dict:
                return JsonResponse(response, safe=False)  # the user already owns this badge / no badges to issue
            return JsonResponse(response.json(), safe=False)  # the user is awarded a new badge

    # def get(self):
    #     t= self.queryset.values()
    #     print(t)





import logging
logging.basicConfig(filename='InsertLocationEvents.log', level=logging.DEBUG)


class InsertLocationEvent(APIView):
    def Logg(self, message):
        logging.debug(message)

    def post(self, request, **kwargs):
        try:
            body_unicode = request.body.decode('utf-8')
            response = json.loads(body_unicode)
            self.Logg(response)
            properties = response['locationeventpertime']
            prop = properties
            user_id = prop['userid']
            accuracy = prop['accuracy']
            latitude = prop['point']['latitude']
            longitude = prop['point']['longitude']
            altitude = prop['point']['altitude']
            timestamp = prop['timestamp']
            bearing = 0
            speed = prop['speed']

            LocationEvent.objects.create(user_id=user_id, accuracy=accuracy, latitude=latitude, longitude=longitude,
                                         altitude=altitude, timestamp=timestamp, bearing=bearing, speed=speed)
        except Exception as e:
            self.Logg(e)
            return HttpResponseBadRequest(e)
        return JsonResponse(response)


class InsertSocialRelation(APIView):
    def Logg(self, title, message):
        logging.debug(title)
        logging.debug(message)

    def post(self, request, **kwargs):
        try:
            body_unicode = request.body.decode('utf-8')
            response = json.loads(body_unicode)
            self.Logg('SocialRelation is : ', response)

            properties = response['socialrelations']
            prop = properties
            user_id = prop['userid']
            user_destination_id = prop['content']['userdestinationid']
            source = prop['source']
            event_type = prop['content']['eventtype']
            value = prop['content']['value']
            timestamp = prop['timestamp']

            SocialRelations.objects.create(user_id=user_id, userDestinationId=user_destination_id, source=source, eventType=event_type,
                                         value=value, timestamp=timestamp)
        except Exception as e:
            self.Logg('Exception :', e)
            return HttpResponseBadRequest(e)
        return JsonResponse(response)


class InsertTouchEvent(APIView):
    def Logg(self, title, message):
        logging.debug(title)
        logging.debug(message)

    def post(self, request, **kwargs):
        try:
            body_unicode = request.body.decode('utf-8')
            response = json.loads(body_unicode)
            self.Logg('TouchEvent is : ', response)

            properties = response['touchevent']
            prop = properties
            user_id = prop['userid']
            timestamp = prop['timestamp']
            value = 1

            TouchEvents.objects.create(user_id=user_id, value=value, timestamp=timestamp)

        except Exception as e:
            self.Logg('Exception :', e)
            return HttpResponseBadRequest(e)
        return JsonResponse(response)


class InsertTimeDiariesAnswers(APIView):
    def Logg(self, title, message):
        logging.debug(title)
        logging.debug(message)

    def post(self, request, **kwargs):
        try:
            body_unicode = request.body.decode('utf-8')
            response = json.loads(body_unicode)
            self.Logg('InsertTimeDiariesAnswers is : ', response)
            properties = response['timediariesanswers']
            user_id = properties['userid']
            answer_duration = properties['answerduration']
            answer_timestamp = properties['answertimestamp']
            notification_timestamp = properties['notificationtimestamp']
            answers = ast.literal_eval(properties['answer'])
            for answer_list in answers:
                answer = answer_list[0]['cnt']
                question = answer_list[0]['qid']
                aid = answer_list[0]['aid']
                cid = answer_list[0]['cid']
                TimeDiaries.objects.create(answer_timestamp=answer_timestamp, user_id=user_id,
                                           answer_duration=answer_duration,
                                           notification_timestamp=notification_timestamp,
                                           question=question, answer=answer, aid=aid, cid=cid)


        except Exception as e:
            self.Logg('Exception :', e)
            return HttpResponseBadRequest(e)
        return JsonResponse(response)


class EnableIncentives(APIView):

    def post(self, request, **kwargs):
        if b'reason' not in request.body:
            return HttpResponseBadRequest("You Must supply reason ")
        if not check_inc_status:

            body_unicode = request.body.decode('utf-8')
            received_json_data = json.loads(body_unicode)
            reason = received_json_data['reason']
            data = {
                  "message_id": 145,
                  "message": "successful operation"
            }
            return JsonResponse(data)
        else:
            return HttpResponseBadRequest("The server is already enabled",status = 403)


class Enquiry(APIView):

    def post(self, request, **kwargs):
        if b'content' not in request.body:
            return HttpResponseBadRequest("You Must supply content ")
        received_json_data = json.loads(request.body)
        app_id = kwargs.get('app_id')
        user_id = kwargs.get('user_id')
        if not check_app(app_id):
           return HttpResponseBadRequest("app id isn't valid")
        if not check_user(user_id):
           return HttpResponseBadRequest("user id isn't valid")
        if "content" in received_json_data:
            Complaint.objects.create(app_id = app_id, user_id = user_id, content = received_json_data['content'])
            return Response('submit completed')
        else:
            return HttpResponseBadRequest(
                content='you mast provide content')


class GetIncentivesCommunity(APIView):
    def get(self, request, **kwargs):
        app_id = kwargs.get('app_id')
        community_id = kwargs.get('community_id')
        if not check_app(app_id):
            return HttpResponseBadRequest("app id isn't valid")
        if not check_community(community_id):
            return HttpResponseBadRequest("community isn't valid")
        data = {
            'community_id': community_id,
            'incentive_type': '2',
            'incentive_quantity': 0.89,
        }
        email = get_user_email_temp(community_id)
        return HttpResponse(email)


class GetAvailableBadges(APIView):
    def get(self, request, **kwargs):
        app_id = kwargs.get('app_id')

        response = get_all_badges_app(app_id)
        if response.get('status_code') != 200:
            return HttpResponse(json.dumps(response),status=response['status_code'])
        return JsonResponse(response)


class GetIncentivesUser(APIView):
    def get(self, request, **kwargs):
        app_id = kwargs.get('app_id')
        user_id = kwargs.get('user_id')
        if not check_user(user_id):
            return HttpResponseBadRequest("user isn't valid")
        user_email = get_user_email(user_id)
        if not user_email:
            return HttpResponseBadRequest("user isn't valid")
        users_badges = get_all_users_badges(user_email)
        badges_response = []
        for badge in users_badges:
            badge_class = badge['badgeclass']
            response = api_call(config_list['url_badgr'] + 'v2/badgeclasses/%s' % badge_class, 'get')

            if response.status_code == 500:
                return HttpResponseBadRequest(response)
            response = response.json()['result']
            if(len(response)) == 0:
                return HttpResponseBadRequest('something wrong')
            response = response[0]
            b = get_badge_details_from_response(response)
            badges_response.append(b)
        #todo: change this!!
        badges_response = [badge for badge in badges_response if badge['app']==app_id]
        data = {
            'app_id': app_id,
            'incentives': {
                'badges': badges_response,
                'messages': []
            }
        }
        return JsonResponse(data, safe=False)


class create_issuer(APIView):
    def post(self,request,**kwargs):
        response = api_call(config_list['url_badgr'] + 'v2/issuers', 'post', json.loads(request.body))

        if response.status_code == 500:
            return HttpResponseBadRequest(response)
        return JsonResponse(response.json(), safe=False, status=response.status_code )


class IncentiveMessagesViewSet(viewsets.ModelViewSet):

    def create(self, request, **kwargs):
        data = is_post_incentive_message_valid(request.data)

        if type(data) == JsonResponse: # 400
            return data
        
        # Generate app if it is yet to exist in lassi
        if len(WeNetApps.objects.filter(app_id=data['app']).all().values()) == 0:
            app_data = {'app_id':data['app'], 'app_name':data['app']}
            app_serializer = WeNetAppsSerializer(data=app_data)
            if app_serializer.is_valid():
                app_serializer.save()

        # Generate a Unique EntityID
        entityId = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(22))
        while IncentiveMessages.objects.filter(entityId=entityId):
            entityId = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(22))

        data['entityId'] = entityId
        serializer = IncentiveMessagesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            r = json.loads(json.dumps(
                {
                    'entityId': entityId,
                    'status_code': 201}))
            return JsonResponse(r, status=201)
        r = json.loads(json.dumps(
            {
                'message': "'An unexpected Validation Error occurred",
                'status_code': 400}))
        return JsonResponse(r, status=400)

    def retrieve(self, request, **kwargs):
        entityId = kwargs.get('entityId')
        msg = IncentiveMessages.objects.filter(entityId=entityId).values()
        r = get_incentive_message_valid(msg)
        return r

    def getAll(self, request, **kwargs):
        msgs = IncentiveMessages.objects.all().values()
        msg_list=[]
        for msg in msgs:
            msg_det=get_incentive_message_detial([msg])
            if msg_det==None:
                return respond_json("Incentive Message not found - Invalid entityId", 404)
            else:
                msg_list.append(msg_det)
        r= {"messages": msg_list,"status_code": 200}
        return JsonResponse(r)
        # return JsonResponse(json.loads(msg_list), status=200)


    def destroy(self, request, **kwargs):
        entityId = kwargs.get('entityId')
        msg = IncentiveMessages.objects.filter(entityId=entityId).values()
        r = get_incentive_message_valid(msg)
        if r.status_code == 404:
            return r
        IncentiveMessages.objects.get(entityId=entityId).delete()
        return r

    def update(self, request, **kwargs):
        try:
            entityId = kwargs['entityId']
            msg = IncentiveMessages.objects.filter(entityId=entityId).values()
            updatedFields = put_incentive_message(entityId, request.data, msg)
        except IndexError:  # 404
            return respond_json("Incentive Message not found - Invalid entityId", 404)

        if type(updatedFields) == JsonResponse:  # 400
            return updatedFields

        IncentiveMessages.objects.filter(entityId=entityId).update(**updatedFields)

        # Unnecessary fields to display
        for key in updatedFields.copy():
            if updatedFields[key] is None:
                del updatedFields[key] 

        r = {'updatedFields': updatedFields,
             "status_code": 200
             }
        return JsonResponse(r, status=200)

    def GET_Issued(self, request, **kwargs):
        issued_msgs=all_issued()
        issued_msgs={"messages": [issued for issued in issued_msgs],'status_code': 200  }
        return JsonResponse(issued_msgs)



class BadgeClass(APIView):

    def post(self, request):
        data = request.data
        app = data.get('app')
        taskTypeId = data.get('taskTypeId')
        label = data.get('label', 'nolabel!')
        threshold = data.get('threshold')

        if type(app) != str or type(taskTypeId) != str or not data['message'] or not type(data['message']) is str or\
                                                     not data['description'] or not type(data['description']) is str:
            return respond_json('app, taskTypeId, description and message are required and must be non-null strings', 400)

        data['criteriaNarrative'] = data.get('message')  # required both in badgr and in Interaction Protocol

        try:
            if threshold < 1:
                raise Exception
        except Exception:
            return respond_json('threshold is required and must to be a positive integer', 400)

        # Prevent duplicate BadgeClasses
        try:
            badges = get_all_badges_app(app)['badges']
        except Exception:
                return respond_json('something went wrong with badger server', 400)


        for badge in badges:
            if badge.get('name') == data.get('name') or (badge['taskTypeId'] == taskTypeId and badge['label'] == label and badge['threshold'] == threshold):
               return respond_json('Duplicate BadgeClass POST aborted - existing name or existing taskTypeId, label and threshold combination', 400) 

        imageUrl = data.get('image')
        checked_image_url = check_image_url(imageUrl)
        if type(checked_image_url) is JsonResponse:
            return checked_image_url  # 403
        data['image'] = checked_image_url

        # due to the fact that badge_class does not support dictionary:
        tags = [f'taskTypeId {taskTypeId}', f'label {label}', f'threshold {threshold}', f'app {app}', f'imageUrl {imageUrl}']
        data['tags'] = tags

        response = api_call(config_list['url_badgr'] + 'v2/issuers/mT7hgXVkQMShRxRWIusVSg/badgeclasses', 'post', data)

        if response.status_code == 500:
            return HttpResponseBadRequest(response)

        if response.status_code == 400:
            return respond_json('Invalid image (incompatible with badgr server)', 400)

        if response.status_code == 413:
            return respond_json('Uploaded image is too large', 413)

        r = json.loads(json.dumps(
            {'entityId': f'{response.json().get("result")[0].get("entityId")}', 'status_code': response.status_code}))
        return JsonResponse(r, status=response.status_code)


    def put(self, request, **kwargs):
        entityId = kwargs.get('entityId')
        badge = getBadgeClass(entityId)
        if type(badge) != dict:
            return badge  # 404 or 500

        put_tup = putBadgeClass(request.data, badge['badge'])
        if type(put_tup) != tuple:
            return put_tup  # 400
        data, updatedFields = put_tup

        response = api_call(config_list['url_badgr'] + 'v2/badgeclasses/' + entityId, 'put', data)

        if response.status_code == 500:
            return HttpResponseBadRequest(response)

        if response.status_code == 400:
            return respond_json('Unexpected Validation Error - Invalid field in body request', 400)

        if response.status_code == 413:
            return respond_json('Uploaded image is too large', 413)

        if response.status_code == 200:
            r = json.loads(json.dumps(
                {'updatedFields': updatedFields, 'status_code': response.status_code}))
            cache.clear()
            return JsonResponse(r, status=response.status_code)


    def get(self, request, **kwargs):
        entityId = kwargs.get('entityId')
        if entityId==None:
            t= get_all_badges()
            return JsonResponse(json.loads(json.dumps(t)), status=200)
        badge = getBadgeClass(entityId)
        if type(badge) != dict:
            return badge  # 404 or 500
        badge['status_code'] = 200
        return JsonResponse(json.loads(json.dumps(badge)), status=badge['status_code'])


    def delete(self, request, **kwargs):
        entityId = kwargs.get('entityId')
        badge = getBadgeClass(entityId)  # in order to return the deleted badge to the caller
        if type(badge) != dict:
            return badge  # 404 or 500

        revoke_assertions = revokeBadgeClassAssertions(entityId)
        if not revoke_assertions is None:
            return revoke_assertions

        # DELETE BadgeClass
        response = api_call(config_list['url_badgr'] + 'v2/badgeclasses/' + entityId, 'delete')

        if response.status_code == 500:
            return HttpResponseBadRequest(response)

        if response.status_code == 204:  # deleted successfully - no content
            badge['status_code'] = 200   # in order to return the deleted badge's details
            return JSONResponse(json.loads(json.dumps(badge)), status=200)


class Assertion(APIView):
    def post(self, request, **kwargs):
        entityId = kwargs.get('entityId')
        response = issue_badge_if_not_exists(request.data, entityId)
        if type(response) == requests.models.Response:
            return JsonResponse(response.json(), safe=False, status=response.status_code)
        # if not Response - User has already got this Badge. (returns dict)
        return JsonResponse(response, safe=False, status=200)


    def get(self,request ,**kwargs):
        entityId = kwargs.get('entityId')
        response = api_call(config_list['url_badgr'] + 'v2/badgeclasses/%s/assertions' % entityId, 'get')

        if response.status_code == 500:
            return HttpResponseBadRequest(response)
        return JsonResponse(response.json(), safe=False, status=response.status_code )
        
