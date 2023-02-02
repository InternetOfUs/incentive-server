# Generated by Django 3.0.6 on 2020-06-01 12:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BadgesUsers',
            fields=[
                ('user_id', models.CharField(max_length=120, primary_key=True, serialize=False)),
                ('app_id', models.CharField(max_length=120)),
                ('first_name', models.CharField(blank=True, max_length=120)),
                ('last_name', models.CharField(blank=True, max_length=120)),
                ('email', models.CharField(blank=True, max_length=120)),
                ('n_discussions', models.IntegerField(default=0)),
                ('n_posts', models.IntegerField(default=0)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
                ('country', models.CharField(max_length=120)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(default=None)),
            ],
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_id', models.CharField(max_length=120)),
                ('user_id', models.CharField(max_length=120)),
                ('content', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LocationEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=120)),
                ('latitude', models.FloatField(default=0)),
                ('longitude', models.FloatField(default=0)),
                ('altitude', models.FloatField(default=0)),
                ('accuracy', models.FloatField(default=0)),
                ('bearing', models.FloatField(default=0)),
                ('speed', models.IntegerField(default=0)),
                ('timestamp', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SocialRelations',
            fields=[
                ('user_id', models.CharField(max_length=120)),
                ('userDestinationId', models.CharField(max_length=120)),
                ('source', models.CharField(max_length=120)),
                ('eventType', models.CharField(max_length=120)),
                ('value', models.IntegerField(default=0)),
                ('timestamp', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tagID', models.IntegerField()),
                ('tagName', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TaskStatus',
            fields=[
                ('user_id', models.CharField(max_length=120)),
                ('community_id', models.CharField(blank=True, default='', max_length=120)),
                ('task_id', models.CharField(max_length=120)),
                ('Action', models.CharField(max_length=120)),
                ('Message_content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='TouchEvents',
            fields=[
                ('user_id', models.CharField(max_length=120)),
                ('value', models.IntegerField(default=1)),
                ('timestamp', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='UsersActivity',
            fields=[
                ('user_id', models.CharField(max_length=120)),
                ('app_id', models.CharField(max_length=120)),
                ('discussion', models.CharField(max_length=120)),
                ('post', models.CharField(max_length=120)),
                ('discussion_id', models.CharField(max_length=120)),
                ('created_at', models.DateTimeField(auto_now_add=True, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Incentive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('schemeID', models.IntegerField(default=0)),
                ('schemeName', models.CharField(blank=True, default='', max_length=100)),
                ('typeID', models.IntegerField(default=0)),
                ('typeName', models.CharField(blank=True, default='', max_length=100)),
                ('status', models.BooleanField(default=True)),
                ('ordinal', models.IntegerField(blank=True, default=0, null=True)),
                ('modeID', models.IntegerField(default=0)),
                ('presentationDuration', models.DateTimeField(auto_now_add=True)),
                ('groupIncentive', models.BooleanField(default=False)),
                ('text', models.TextField()),
                ('condition', models.TextField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incentive', to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(blank=True, null=True, to='incentive.Tag')),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('docfile', models.FileField(upload_to='documents/%Y/%m/%d')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='document', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]