# Generated by Django 3.0.6 on 2020-06-07 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incentive', '0007_wenetusers_made_up'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wenetusers',
            old_name='tweeter_follows',
            new_name='relations',
        ),
        migrations.RemoveField(
            model_name='wenetusers',
            name='tweeter_likes',
        ),
    ]
