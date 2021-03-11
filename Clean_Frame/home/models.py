from django.db import models
from django.contrib.auth.models import User

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
    profile_created=models.DateTimeField(auto_now=True)
    account_banned_permanent=models.BooleanField(default=False)
    account_banned_temporary=models.BooleanField(default=False)
    account_ban_date=models.DateTimeField(blank=True, null=True)
    account_ban_time=models.IntegerField(default=0)
    signup_date=models.DateTimeField(auto_now=True)
    verified=models.BooleanField(default=False)
    otp_time=models.DateTimeField(auto_now=True)
    otp=models.CharField(max_length=100, null=True)

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
    profile_created=models.DateTimeField(auto_now=True)
    account_banned_permanent=models.BooleanField(default=False)
    account_banned_temporary=models.BooleanField(default=False)
    account_ban_date=models.DateTimeField(blank=True, null=True)
    account_ban_time=models.IntegerField(default=0)
    signup_date=models.DateTimeField(auto_now=True)
    verified=models.BooleanField(default=False)
    otp_time=models.DateTimeField(auto_now=True)
    otp=models.CharField(max_length=100, null=True)
    stipend=models.FloatField(default=0, null=True)
    internship_duration=models.IntegerField(default=0, null=True)
    students_required=models.IntegerField(default=0, null=True)
    internship_position=models.CharField(max_length=100, null=True)
    minimum_cgpa=models.FloatField(default=5.0, null=True)
    prerequisite=models.CharField(max_length=1000000, null=True)

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'
