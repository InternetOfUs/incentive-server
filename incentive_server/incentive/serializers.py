__author__ = 'Daniel'
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Incentive, Tag, WeNetUsers, TaskStatus, WeNetApps, IncentiveMessages, UsersCohorts
import logging

logger = logging.getLogger('incentive_server')


class UsersCohortsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersCohorts
        fields = '__all__'


class WeNetUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeNetUsers
        fields = '__all__'


class WeNetAppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeNetApps
        fields = '__all__'


#class IncentiveAppSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = IncentiveApp
#        fields = '__all__'


class IncentiveMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncentiveMessages
        fields = '__all__'


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        community_id = serializers.CharField(write_only=True, required=False)
        fields = '__all__'

        # extra_kwargs = {
        #     'community_id': {
        #         # Tell DRF that the link field is not required.
        #         'default': None
        #     }
        # }



class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')



class UserSerializer(serializers.ModelSerializer):
    incentive = serializers.PrimaryKeyRelatedField(many=True, queryset=Incentive.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'incentive')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tagID', 'tagName')


class IncentiveSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True,  read_only=False)
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Incentive
        fields = ('owner','schemeName', 'schemeID','text','typeID','typeName','status','ordinal','tags','modeID',
        'groupIncentive','condition')

    def create(self, validated_data):
     #   logger.info(validated_data)
        tags_data = validated_data.pop('tags',[])
        incentive = super(IncentiveSerializer, self).create(validated_data)
        for tag in tags_data:
            if tag is not None:
                tags_ids = [tag["tagID"] for tag in tags_data if "tagID" in tag]
                if tags_ids is None:
                    #Tag.objects.create(incentiveID=incentive,**tag)
                    Tag.objects.create(**tag)

        # Ignores tags without a tagId
        #tags_ids = [tag["incentiveID"] for tag in tags_data if "incentiveID" in tag]
        tags_ids = [tag["tagID"] for tag in tags_data if "tagID" in tag]

        if tags_ids:
            tags = Tag.objects.filter(tagID__in=tags_ids)
            incentive.tags.add(*tags)

        logger.info("added new incentive:"+str(incentive))

        return incentive


#class BadgeSteeringIncentiveMessageSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = BadgeSteeringIncentiveMessage
#        fields = '__all__'
