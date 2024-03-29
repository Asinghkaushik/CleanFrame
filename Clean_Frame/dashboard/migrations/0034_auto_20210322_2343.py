# Generated by Django 2.2.19 on 2021-03-22 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0033_auto_20210322_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffpermissions',
            name='can_give_notifications',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staffpermissions',
            name='can_manage_staff_accounts',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staffpermissions',
            name='can_manage_technical_support',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='staffpermissions',
            name='can_manage_blogs',
            field=models.BooleanField(default=False),
        ),
    ]
