# Generated by Django 3.0.6 on 2021-08-22 06:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('incentive', '0034_auto_20210819_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgesteeringincentivemessage',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
