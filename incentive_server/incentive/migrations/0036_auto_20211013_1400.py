# Generated by Django 3.0.6 on 2021-10-13 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incentive', '0035_badgesteeringincentivemessage_createdat'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskstatus',
            name='taskId',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AlterField(
            model_name='badgesteeringincentivemessage',
            name='inactivity_period',
            field=models.PositiveIntegerField(blank=True),
        ),
    ]
