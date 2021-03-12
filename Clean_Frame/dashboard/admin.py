from django.contrib import admin
from .models import StaffPermissions, CompanyAnnouncement, Result, StudentRegistration
# Register your models here.
admin.site.register(StaffPermissions)
admin.site.register(CompanyAnnouncement)
admin.site.register(Result)
admin.site.register(StudentRegistration)
