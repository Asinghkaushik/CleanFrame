# Generated by Django 2.2.19 on 2021-03-21 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0024_companyannouncement_last_round_result_announced'),
    ]

    operations = [
        migrations.AddField(
            model_name='internship',
            name='result_announced',
            field=models.BooleanField(default=False),
        ),
    ]
