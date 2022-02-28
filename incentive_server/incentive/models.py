from django.db import models
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
# Create your models here.
from django.contrib import admin
import random

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())


class Tag(models.Model):
    #incentiveID = models.ForeignKey(Incentive,related_name="tags")
    tagID = models.IntegerField(null=False)
    tagName = models.CharField(max_length=100)


    # class Meta:
    #     unique_together = ('incentiveID','tagID')



    def __unicode__(self):
         return '%d: %s' % (self.tagID, self.tagName)


class IssuedIncentives(models.Model):
    created = models.DateTimeField(auto_now_add=True, primary_key=True)
    user_id = models.CharField(max_length=120)
    app_id = models.CharField(max_length=120)
    incentive_id = models.CharField(max_length=120)
    type = models.CharField(max_length=120)
    delivered = models.BooleanField(default=False)


class TimeDiaries(models.Model):
    user_id = models.CharField(max_length=120)
    intervention_id = models.IntegerField(null=True, blank=True, default=0)
    answer_duration = models.IntegerField()
    notification_timestamp = models.CharField(max_length=255)
    answer_timestamp = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    aid = models.CharField(max_length=255)
    cid = models.CharField(max_length=255)

    class Meta:
        unique_together = (('question', 'answer','answer_timestamp'),)


class Complaint(models.Model):
    app_id = models.CharField(max_length=120)
    user_id = models.CharField(max_length=120)
    content = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)


class LocationEvent(models.Model):
    user_id = models.CharField(max_length=120)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    altitude = models.FloatField(default=0)
    accuracy = models.FloatField(default=0)
    bearing = models.FloatField(default=0)
    speed = models.IntegerField(default=0)
    timestamp = models.CharField(max_length=255)
    intervention_id = models.IntegerField(null=True, blank=True, default=0)


class SocialRelations(models.Model):
    user_id = models.CharField(max_length=120)
    userDestinationId = models.CharField(max_length=120)
    source = models.CharField(max_length=120)
    eventType = models.CharField(max_length=120)
    value = models.IntegerField(default=0)
    timestamp = models.CharField(max_length=255, primary_key=True)
    intervention_id = models.IntegerField(null=True, blank=True, default=0)


class TaskStatus(models.Model):
    user_id = models.CharField(max_length=120)
    community_id = models.CharField(max_length=120, default='', blank=True)
    app_id = models.CharField(max_length=120, blank=False)
    taskTypeId = models.CharField(max_length=120)
    label = models.CharField(max_length=120, default='nolabel!', blank=True)
    count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, primary_key=True)
    intervention_id = models.IntegerField(null=True, blank=True, default=0)
    taskId = models.CharField(max_length=120, blank=True, null=True)


class TouchEvents(models.Model):
    user_id = models.CharField(max_length=120)
    value = models.IntegerField(default=1)
    timestamp = models.CharField(max_length=255, primary_key=True)
    intervention_id = models.IntegerField(null=True, blank=True, default=0)


class UsersCohorts(models.Model):
    user_id = models.CharField(max_length=120)
    app_id = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=120, blank=False)
    cohort = models.IntegerField(default=0)
    class Meta:
        unique_together = (('user_id', 'app_id'))


class WeNetUsers(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    user_id = models.CharField(max_length=120, primary_key=True)
    app_id = models.CharField(max_length=120)
    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120, blank=True)
    email = models.CharField(max_length=120, blank=True)

    diaries_answers = models.IntegerField(default=0)
    touch_events = models.IntegerField(default=0)
    relations = models.IntegerField(default=0)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    country = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(default=None)
    made_up = models.IntegerField(default=0)
    class Meta:
        unique_together = (('user_id', 'app_id'))

#class MessagesFamily(models.Model):
#    id = models.AutoField(primary_key=True)
#    family = models.CharField(max_length=100, unique=True)
#    condition_repeat = models.IntegerField(default=2)
#    condition_frequency = models.IntegerField(default=3)
#    condition_inactivity = models.IntegerField(default=2)


class WeNetApps(models.Model):
    app_id = models.CharField(max_length=100, unique=True,primary_key=True)
    app_name = models.CharField(max_length=100,)
    def __unicode__(self):
         return self.app_name

#class IncentiveMessages(models.Model):
#    id = models.AutoField(primary_key=True)
#    created = models.DateTimeField(auto_now_add=True)
#    status = models.BooleanField(default=True)
#    family = models.ForeignKey(MessagesFamily, on_delete=models.CASCADE, to_field='family', verbose_name='family')
#    groupIncentive = models.BooleanField(default=False)
#    message = models.TextField()


#class IncentiveApp(models.Model):
#    incentive = models.ForeignKey(IncentiveMessages, null=False, on_delete=models.CASCADE)
#    app_id = models.ForeignKey(WeNetApps, null=False, on_delete=models.CASCADE)


#class IncentiveAppInline(admin.TabularInline):
#    model = IncentiveApp
#    fields = ('incentive', 'app_id')

#class MessageTag(models.Model):
#    incentive = models.ForeignKey(IncentiveMessages, null=False, on_delete=models.CASCADE)
#    id = models.AutoField(primary_key=True)
#    tag_name = models.CharField(max_length=100, db_index=True)
#    tag_value = models.CharField(max_length=100, db_index=True)
#    # class Meta:
#        #     unique_together = ('incentiveID','tagID')

    def __unicode__(self):
         return '%d: %s' % (self.id, self.name)


#class MessageTagInline(admin.TabularInline):
#    model = MessageTag
#    fields = ('tag_name', 'tag_value')

#class IncentiveMessagesAdmin(admin.ModelAdmin):
#    inlines = [
#        MessageTagInline, IncentiveAppInline
#    ]


#admin.site.register(IncentiveMessages, IncentiveMessagesAdmin)



class Incentive(models.Model):
    owner = models.ForeignKey('auth.User', models.CASCADE, related_name='incentive')
    # highlighted = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    schemeID= models.IntegerField(default=0)
    schemeName = models.CharField(max_length=100, blank=True, default='')
    typeID=models.IntegerField(default=0)
    typeName=models.CharField(max_length=100,blank=True,default='')
    status=models.BooleanField(default=True)
    ordinal=models.IntegerField(null=True,blank=True,default=0)
    modeID=models.IntegerField(default=0)
    presentationDuration=models.DateTimeField(auto_now_add=True)
    groupIncentive=models.BooleanField(default=False)
    text =models.TextField()
    #image =models.ImageField()
    condition=models.TextField()
    tags = models.ManyToManyField(Tag, related_name="tags")
   # code = models.TextField()
  #  language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    #email = models.TextField()

    class Meta:
        ordering = ('created',)

    def user_can_manage_me(self, user):
        return user == self.owner
    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        #lexer = get_lexer_by_name(self.language)
        #options = self.schemeName and {'title': self.schemeName} or {}
       # formatter = HtmlFormatter(text=self.text,
      #                        full=True, **options)
     #   self.highlighted = highlight(self.schemeName, lexer, formatter)
        super(Incentive, self).save(*args, **kwargs)

    def __unicode__(self):
         return '%d: %s' % (self.schemeID, self.schemeName)

class Document(models.Model):
    owner = models.ForeignKey('auth.User',models.CASCADE, related_name='document')
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')


class IncentiveMessages(models.Model):
    id = models.AutoField(primary_key=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    entityId = models.CharField(max_length=22)
    taskTypeId = models.CharField(max_length=120)
    label = models.CharField(max_length=120)
    max_repeat = models.PositiveIntegerField()
    frequency = models.PositiveIntegerField()
    inactivity_period = models.PositiveIntegerField(null=True, blank=True)
    inactivity_range_top = models.PositiveIntegerField(null=True, blank=True)
    inactivity_range_bottom = models.PositiveIntegerField(null=True, blank=True)
    app = models.CharField(max_length=120)
    message = models.TextField()



