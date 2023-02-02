# from django.conf.urls import patterns, include, url

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, routers
from django.conf.urls import url
from incentive import views
from incentive import runner
from incentive.views import IncetiveViewSet, IncentiveMessagesViewSet
from rest_framework import renderers
from django.conf.urls import  url
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

admin.site.site_header = 'Incentive Server'
admin.site.site_title = 'Incentive Server'
admin.site.index_title = 'Admin'
# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
incentive_list = IncetiveViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
incentive_detail = IncetiveViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
incentive_messages = IncentiveMessagesViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'post': 'create',
    'delete': 'destroy'
})
incentive = IncetiveViewSet.as_view({
    'get': 'highlight'
}, renderer_classes=[renderers.StaticHTMLRenderer])

user_list = UserViewSet.as_view({
    'get': 'list'
})
user_detail = UserViewSet.as_view({
    'get': 'retrieve'
})

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'incentive', views.IncetiveViewSet)
router.register(r'users', UserViewSet)
router.register(r'WeNetUsers', views.WeNetUsersViewSet)
router.register(r'TaskStatus', views.TaskStatusViewSet)
router.register(r'WeNetApps', views.WeNetAppsViewSet)
#router.register(r'IncentiveApp', views.IncentiveAppViewSet)
router.register(r'UsersCohorts', views.UsersCohortsViewSet)


task_router = routers.DefaultRouter()
task_router.register(r'TaskTypeStatus', views.TaskStatusViewSet)
task_router.register(r'TaskTransactionStatus', views.TaskStatusViewSet)


# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
# url(r'^docs/', include('rest_framework_swagger.urls')),
urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^about/$', views.about),
    url(r'^api/StartIncentivesMassages/', views.debug_messages),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^$', views.home, name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^incentives/$', views.incetive_list, name='incetive_filter'),
    url(r'^login/$', views.login, name='login'),
    url(r'^wiki/$', views.wiki, name='wiki'),
    url(r'^aboutus/', views.aboutus, name='aboutus'),
    url(r'^list/$', views.list, name='data_set'),
    url(r'^profile/', views.userProfile, name='profile_page'),
    url(r'^startAlg/', runner.startAlg, name='startAlg'),
    url(r'^predicting/', runner.getTheBestForTheUser, name='predicting'),

    url(r'^getIncUser/$', views.getUserID, name='getIncUser'),

    url(r'^dash/pages/dash.html', views.dash, name='dash'),
    url(r'^badgesdash/pages/dash.html', views.badgesdash, name='dash'),

    # url(r'^dashStream/$', views.dashStream, name='dashStream'),

    url(r'^dash/pages/streamResponse/', views.stream_response, name='streamResponse'),
    url(r'^mark_latest_id/$', views.mark_latest_id, name='mark_latest_id'),
    url(r'^new_classifications/$', views.get_new_classifications, name='new_classifications'),
    url(r'^new_classifications_test/$', views.get_new_classifications_test, name='new_classifications'),
    url(r'^disratio/$', views.GiveRatio, name='disratio'),
    url(r'^add_event/$', views.receive_event, name='receive_event'),
    url(r'^hello/$', views.receive_event, name='receive_event'),
    url(r'^incentive/disable_incentive/?$', views.DisableIncentives.as_view(), name='disable incentive'),
    url(r'^incentive/enable_incentive/?$', views.EnableIncentives.as_view(), name='enable incentive'),
    url(r'^incentive/apps/(?P<app_id>[^/]+)/community/(?P<community_id>[^/]+)/?$',
        views.GetIncentivesCommunity.as_view(), name='get_incentives_community'),
    url(r'^incentive/apps/(?P<app_id>[^/]+)/users/(?P<user_id>[^/]+)/?$',
        views.GetIncentivesUser.as_view(), name='get_incentives_user'),

    url(r'^Tasks/', include(task_router.urls)),
    url(r'Stream/locationevent', views.InsertLocationEvent.as_view()),
    url(r'Stream/SocialRelation', views.InsertSocialRelation.as_view()),
    url(r'Stream/TouchEvent', views.InsertTouchEvent.as_view()),
    url(r'Stream/TimeDiariesAnswers', views.InsertTimeDiariesAnswers.as_view()),

    url(r'^enquiry_incentives/apps/(?P<app_id>[^/]+)/users/(?P<user_id>[^/]+)/?$',
        views.Enquiry.as_view(), name='enquiry_incentives'),
    url(r'^badges/apps/(?P<app_id>[^/]+)/?$',
        views.GetAvailableBadges.as_view(), name='get_badges_app'),
    url(r'^badges/issuers/?$',
        views.create_issuer.as_view(), name='create issuer'),

   # url(r'^badges/issuers/(?P<entityId>[^/]+)/BadgeClasses/?$',
    #    views.CRU_badgeClass.as_view(), name='CRU_badgeClass-issuer_post'),

    url(r'^badges/BadgeClasses/TaskType/?$',
        views.BadgeClass.as_view(), name='POST_TaskTypeBadgeClass'),
    url(r'^badges/BadgeClasses/TaskType/(?P<entityId>[^/]+)/?$',
        views.BadgeClass.as_view(), name='PUT_TaskTypeBadgeClass'),
    url(r'^badges/BadgeClasses/TaskTransaction/?$',
        views.BadgeClass.as_view(), name='POST_TaskTransactionBadgeClass'),
    url(r'^badges/BadgeClasses/TaskTransaction/(?P<entityId>[^/]+)/?$',
        views.BadgeClass.as_view(), name='PUT_TaskTransactionBadgeClass'),

    url(r'^badges/BadgeClasses/(?P<entityId>[^/]+)/?$',
        views.BadgeClass.as_view(), name='GET-DELETE_BadgeClass'),
    url(r'^badges/BadgeClasses/',
        views.BadgeClass.as_view(), name='GET-BadgeClass'),

    url(r'^badges/BadgeClasses/(?P<entityId>[^/]+)/assertions/?$',
        views.Assertion.as_view(), name='assertion badge'),

    url(r'^messages/Issued/?$',
        views.IncentiveMessagesViewSet.as_view({'get':'GET_Issued'}), name='GET-Issued_IncentiveMessage'),
        
    url(r'^messages/TaskType/(?P<entityId>[^/]+)/?$',
        views.IncentiveMessagesViewSet.as_view({'put':'update'}), name='PUT_TaskTypeIncentiveMessage'),
    url(r'^messages/TaskType/?$',
        views.IncentiveMessagesViewSet.as_view({"get":"getAll",'post':'create'}), name='POST_TaskTypeIncentiveMessage'),
    url(r'^messages/TaskTransaction/?$',
        views.IncentiveMessagesViewSet.as_view({'post':'create'}), name='POST_TaskTransactionIncentiveMessage'),
    url(r'^messages/TaskTransaction/(?P<entityId>[^/]+)/?$',
        views.IncentiveMessagesViewSet.as_view({'put':'update'}), name='PUT_TaskTransactionIncentiveMessage'),
    url(r'^messages/(?P<entityId>[^/]+)/?$',
        views.IncentiveMessagesViewSet.as_view({'get':'retrieve', 'delete':'destroy'}), name='GET-DELETE_IncentiveMessage'),

    url(r'^test_func/$', views.test_func, name='test_func'),
    url(r'^test_post/$', views.TestPost.as_view(), name='test_post'),



]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

