# Generated by Django 2.2.19 on 2021-03-10 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20210310_1745'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyannouncement',
            name='round_name',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]