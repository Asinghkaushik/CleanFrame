from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class StaffPermissions(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    can_access_student_inactive_accounts=models.BooleanField(default=False)
    can_access_company_inactive_accounts=models.BooleanField(default=False)
    can_ban_users=models.BooleanField(default=False)
    can_delete_staff_accounts=models.BooleanField(default=False)
    can_unban_users=models.BooleanField(default=False)
    can_create_new_company_account=models.BooleanField(default=False)
    can_manage_blogs=models.BooleanField(default=True)
    
    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'

class Internship(models.Model):
    company=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    internship_name=models.CharField(max_length=10000, null=True)
    stipend=models.FloatField(default=0, null=True)
    internship_duration=models.IntegerField(default=0, null=True)
    students_required=models.IntegerField(default=0, null=True)
    internship_position=models.CharField(max_length=100, null=True)
    minimum_cgpa=models.FloatField(default=5.0, null=True)
    prerequisite=models.CharField(max_length=1000000, null=True)
    result_announced=models.BooleanField(default=False)

    def __str__(self):
        if self.company:
            return self.company.username + str(" -> ") + self.internship_name
        else:
            return 'NILL'
        
class InternshipFinalResult(models.Model):
    internship=models.ForeignKey(Internship, on_delete=models.CASCADE, null=True, blank=True)
    company=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='company')
    student=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='student')
    student_agrees=models.BooleanField(default=False)
    
    def __str__(self):
        if self.internship:
            if self.student:
                return str(self.student) + " is an intern in " + str(self.internship)
            else:
                return str(self.internship)
        else:
            if self.student:
                return str(self.student)
            else:
                return "NIL"

class CompanyAnnouncement(models.Model):
    internship=models.ForeignKey(Internship, on_delete=models.CASCADE, null=True, blank=True)
    company=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    general_announcement=models.BooleanField(default=False)
    internship_round=models.CharField(max_length=100, null=True)
    round_name=models.CharField(max_length=1000, null=True)
    first_round=models.BooleanField(default=False)
    last_round=models.BooleanField(default=False)
    last_round_result_announced=models.BooleanField(default=False)
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

# class Result(models.Model):
#     company=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='company')
#     student=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='student')
#     internship_round=models.CharField(max_length=100, null=True)

#     def __str__(self):
#         if self.company:
#             if self.student:
#                 return str(self.student) + " cleared round " + str(self.internship_round) + " of " + str(self.company)
#             else:
#                 return str(self.company)
#         else:
#             if self.student:
#                 return str(self.student)
#             else:
#                 return "NIL"

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
    date_of_registrations=models.DateTimeField(auto_now=True)
    result_status=models.IntegerField(default=0)
    internship_cleared=models.BooleanField(default=False)
    #Status 0 : Not Announced
    #Status 1: Cleared
    #Status 2: Rejected

    def __str__(self):
        return str(self.student.username) + " registered in " + str(self.company)

class ProfilePermissions(models.Model):
    user_who_can_see=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='can_see')
    user_whose_to_see=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='whose_to_see')


    def __str__(self):
        if self.user_who_can_see:
            if self.user_whose_to_see:
                return str(self.user_who_can_see) + " can see " + str(self.user_whose_to_see) + " profile"
            else:
                return str(self.user_who_can_see)
        else:
            if self.user_whose_to_see:
                return str(self.user_whose_to_see)
            else:
                return "NIL"

class Blog(models.Model):
    topic=models.CharField(max_length=100000)
    short_description=models.CharField(max_length=100000000)
    brief_description=models.TextField()
    file=models.FileField(upload_to='post_files/', null=True, blank=True)
    
    def __str__(self):
        return self.topic