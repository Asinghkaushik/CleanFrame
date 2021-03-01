from django.db import models
from django.contrib.auth.models import User

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
