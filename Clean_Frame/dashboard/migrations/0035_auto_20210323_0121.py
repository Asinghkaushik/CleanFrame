# Generated by Django 2.2.19 on 2021-03-23 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0034_auto_20210322_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='internshipfinalresult',
            name='student_agrees',
            field=models.IntegerField(default=0),
        ),
    ]
