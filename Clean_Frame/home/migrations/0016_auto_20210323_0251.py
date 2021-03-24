# Generated by Django 2.2.19 on 2021-03-23 02:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_auto_20210323_0210'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='got_internship',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='companyprofile',
            name='otp_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 23, 2, 51, 16, 623393)),
        ),
        migrations.AlterField(
            model_name='companyprofile',
            name='profile_created',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 23, 2, 51, 16, 623312)),
        ),
        migrations.AlterField(
            model_name='companyprofile',
            name='signup_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 23, 2, 51, 16, 623371)),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='otp_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 23, 2, 51, 16, 622378)),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='profile_created',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 23, 2, 51, 16, 622298)),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='signup_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 23, 2, 51, 16, 622358)),
        ),
    ]