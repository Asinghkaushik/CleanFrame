# Generated by Django 2.2.19 on 2021-03-12 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_internship'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyannouncement',
            name='internship',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.Internship'),
        ),
    ]