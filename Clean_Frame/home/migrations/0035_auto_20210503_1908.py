# Generated by Django 3.0.8 on 2021-05-03 13:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0034_auto_20210327_2354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyprofile',
            name='otp_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 3, 19, 8, 51, 823058)),
        ),
        migrations.AlterField(
            model_name='companyprofile',
            name='profile_created',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 3, 19, 8, 51, 822956)),
        ),
        migrations.AlterField(
            model_name='companyprofile',
            name='signup_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 3, 19, 8, 51, 823035)),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='otp_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 3, 19, 8, 51, 822056)),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='profile_created',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 3, 19, 8, 51, 821961)),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='signup_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 3, 19, 8, 51, 822031)),
        ),
    ]
