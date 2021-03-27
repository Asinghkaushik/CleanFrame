from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class StudentProfile(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    contact_number=models.IntegerField(null=True)
    image=models.ImageField(upload_to='post_images/', default="us_ma.png")
    cv=models.FileField(upload_to='post_files/', null=True, blank=True)
    cgpa=models.FloatField(default=0.0, null=True)
    complete_address=models.CharField(max_length=1000, null=True)
    gender=models.CharField(max_length=100, null=True)
    profile_filled=models.BooleanField(default=False)
    profile_created=models.DateTimeField(default=datetime.datetime.now())
    account_banned_permanent=models.BooleanField(default=False)
    account_banned_temporary=models.BooleanField(default=False)
    account_ban_date=models.DateTimeField(blank=True, null=True)
    account_ban_time=models.IntegerField(default=0)
    signup_date=models.DateTimeField(default=datetime.datetime.now())
    verified=models.BooleanField(default=False)
    otp_time=models.DateTimeField(default=datetime.datetime.now())
    otp=models.CharField(max_length=100, null=True)
    got_internship=models.BooleanField(default=False)

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'

class CompanyProfile(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    contact_number=models.IntegerField(null=True)
    complete_address=models.CharField(max_length=1000, null=True)
    image=models.ImageField(upload_to='post_images/', default="us_ma.png")
    profile_filled=models.BooleanField(default=False)
    profile_created=models.DateTimeField(default=datetime.datetime.now())
    account_banned_permanent=models.BooleanField(default=False)
    account_banned_temporary=models.BooleanField(default=False)
    account_ban_date=models.DateTimeField(blank=True, null=True)
    account_ban_time=models.IntegerField(default=0)
    signup_date=models.DateTimeField(default=datetime.datetime.now())
    verified=models.BooleanField(default=False)
    otp_time=models.DateTimeField(default=datetime.datetime.now())
    otp=models.CharField(max_length=100, null=True)

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'

class Query(models.Model):
    email=models.CharField(max_length=1000, null=True)
    query=models.TextField()
    date_of_query=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.email