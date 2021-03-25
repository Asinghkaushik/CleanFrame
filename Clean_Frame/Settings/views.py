from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import (login,authenticate,logout)
from django.conf import settings
from django.core.mail import send_mail
import math,random,string,array,secrets,datetime
from twilio.rest import Client
from home.models import CompanyProfile,StudentProfile
from dashboard.forms import StudentPhotoForm,StudentCVForm
from  dashboard.models import StaffPermissions
from os import urandom
from random import choice

# Create your views here.

def SEND_OTP_TO_PHONE(mobile_number, country_code, message):
    client = Client(settings.PHONE_ACCOUNT_SID_TWILIO, settings.PHONE_ACCOUNT_AUTH_TOKEN_TWILIO)
    message = client.messages.create(
                        body=str(message),
                        from_= settings.PHONE_NUMBER_TWILIO,
                        to=str(country_code)+str(mobile_number)
                    )

def SENDMAIL(subject, message, email):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    send_mail( subject, message, email_from, recipient_list )

def generate_otp():
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    OTP = ""
    for i in range(7) :
        OTP += digits[math.floor(random.random() * 62)]
    return OTP

def get_my_profile(request):
    data={}
    try:
        data=StudentProfile.objects.get(user=request.user)
    except:
        try:
            data=CompanyProfile.objects.get(user=request.user)
        except:
            data={}
    return data

def get_permissions(request):
    try:
        permissions = StaffPermissions.objects.get(user=request.user)
    except:
        StaffPermissions.objects.create(user=request.user)
        permissions = StaffPermissions.objects.get(user=request.user)
    return permissions

def error_code(request, message):
    return render(request,"home/error_code.html",context={"error": message})

def error_message(request, message):
    return render(request,"home/error_message.html",context={"error": message})

def error_detection(request,id):
    if request.user.is_authenticated==False:
        return redirect('home')
    if request.user.is_staff or request.user.is_superuser:
        return False
    if request.user.is_active==False:
        return error_code(request,"500")
    if request.user.last_name==settings.COMPANY_MESSAGE:
        try:
            p=CompanyProfile.objects.get(user=request.user)
        except:
            return error_message(request,"Profile Not Found")
    else:
        try:
            p=StudentProfile.objects.get(user=request.user)
        except:
            return error_message(request,"Profile Not Found")
    if p.account_banned_permanent:
        return error_message(request,"Your account is banned permanently")
    if p.account_banned_temporary:
        return error_message(request,"Your account is banned temporarily, login again")
    if p.profile_filled==False and id==1:
        return redirect('profile')
    return False



def settings_home(request):
    if error_detection(request,1)==False:
        data=get_my_profile(request)
        return render(request,'Settings/settings.html',context={"data": data, "permissions": get_permissions(request)})
    return error_detection(request,1)

# def delete_account(request):
#     if error_detection(request,1)==False:
#         try:
#             u=User.objects.get(username=request.user)
#             email=u.email
#             u.delete()
#         except:
#             return error_message(request,"User Not Found")
#         subject = 'Account Deletion Notice'
#         message = f'Hey, user!\nYour account has been sucessfully deleted from Clean Frame.\nMoreover all the records related are also deleted.\nIf you create a new account then previous effects or changes would not be shown.\nThanks'
#         SENDMAIL(subject,message,email)
#         return redirect('home')
#     return error_detection(request,1)