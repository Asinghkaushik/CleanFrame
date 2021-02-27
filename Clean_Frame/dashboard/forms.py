from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from home.models import CompanyProfile, StudentProfile

class StudentPhotoForm(ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            "image"
        ]

class StudentCVForm(ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            "cv"
        ]