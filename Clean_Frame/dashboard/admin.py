from django.contrib import admin
from .models import StaffPermissions, CompanyAnnouncement, InternshipFinalResult, StudentRegistration, Internship, ProfilePermissions,Blog
from .models import TechnicalSupportRequest, TechnicalSupportResponse, Notification
# Register your models here.
admin.site.register(StaffPermissions)
admin.site.register(CompanyAnnouncement)
admin.site.register(InternshipFinalResult)
admin.site.register(StudentRegistration)
admin.site.register(Internship)
admin.site.register(ProfilePermissions)
admin.site.register(Blog)
admin.site.register(TechnicalSupportRequest)
admin.site.register(TechnicalSupportResponse)
admin.site.register(Notification)
