from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class StaffPermissions(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    can_access_student_inactive_accounts=models.BooleanField(default=False)
    can_access_company_inactive_accounts=models.BooleanField(default=False)

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'

class CompanyAnnouncement(models.Model):
    company=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    general_announcement=models.BooleanField(default=False)
    internship_round=models.CharField(max_length=100, null=True)
    round_name=models.CharField(max_length=1000, null=True)
    first_round=models.BooleanField(default=False)
    prev_round_for_result=models.CharField(max_length=100, null=True)
    last_date_to_apply=models.DateTimeField(default=datetime.datetime.now)
    announcement_date=models.DateTimeField(auto_now=True)
    message=models.CharField(max_length=100000)
    file=models.FileField(upload_to='post_files/', null=True, blank=True)
    file_for_prev_result=models.FileField(upload_to='post_files/', null=True, blank=True)

    def __str__(self):
        if self.company:
            return str(self.company.username) + " Round " + str(self.internship_round)
        else:
            return 'NILL'
        
class Result(models.Model):
    company=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='company')
    student=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='student')
    internship_round=models.CharField(max_length=100, null=True)
    
    def __str__(self):
        if self.company:
            if self.student:
                return str(self.student) + " cleared round " + str(self.internship_round) + " of " + str(self.company)
            else:
                return str(self.company)
        else:
            if self.student:
                return str(self.student)
            else:
                return "NIL"
            
class ProfileVisibilty(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    to_other_student=models.BooleanField(default=True)
    to_company=models.BooleanField(default=True)

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'
        
class StudentRegistration(models.Model):
    company=models.ForeignKey(CompanyAnnouncement, on_delete=models.CASCADE, null=True, blank=True)
    student=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return str(self.student.username) + "registered in " + str(self.company)