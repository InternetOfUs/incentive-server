# Generated by Django 3.0.6 on 2020-06-07 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incentive', '0005_auto_20200601_1419'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeNetUsers',
            fields=[
                ('user_id', models.CharField(max_length=120, primary_key=True, serialize=False)),
                ('app_id', models.CharField(max_length=120)),
                ('first_name', models.CharField(blank=True, max_length=120)),
                ('last_name', models.CharField(blank=True, max_length=120)),
                ('email', models.CharField(blank=True, max_length=120)),
                ('diaries_answers', models.IntegerField(default=0)),
                ('touch_events', models.IntegerField(default=0)),
                ('tweeter_follows', models.IntegerField(default=0)),
                ('tweeter_likes', models.IntegerField(default=0)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
                ('country', models.CharField(max_length=120)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(default=None)),
            ],
        ),
        migrations.DeleteModel(
            name='BadgesUsers',
        ),
    ]