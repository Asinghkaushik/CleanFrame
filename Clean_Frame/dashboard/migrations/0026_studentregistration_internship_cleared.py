# Generated by Django 2.2.19 on 2021-03-21 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0025_internship_result_announced'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentregistration',
            name='internship_cleared',
            field=models.BooleanField(default=False),
        ),
    ]