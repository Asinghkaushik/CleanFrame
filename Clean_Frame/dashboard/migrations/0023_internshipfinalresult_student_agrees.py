# Generated by Django 2.2.19 on 2021-03-21 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0022_auto_20210321_0752'),
    ]

    operations = [
        migrations.AddField(
            model_name='internshipfinalresult',
            name='student_agrees',
            field=models.BooleanField(default=False),
        ),
    ]