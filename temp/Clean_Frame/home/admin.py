from django.contrib import admin
from .models import StudentProfile, CompanyProfile
# Register your models here.
admin.site.register(StudentProfile)
admin.site.register(CompanyProfile)