from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import (login,authenticate,logout)
from django.conf import settings 
from django.core.mail import send_mail 
import math,random,string,datetime
from twilio.rest import Client
from home.models import CompanyProfile,StudentProfile

# Create your views here.
def dashboard(request):
    if error_detection(request,1)==False:
        return HttpResponse('Dashboard')
    return error_detection(request,1)

def error_detection(request,id):
    print(request.user.is_authenticated)
    if request.user.is_authenticated==False:
        return redirect('home')
    if request.user.is_staff or request.user.is_superuser:
        return False
    if request.user.is_active==False:
        return HttpResponse("Account's associated email is not otp verified")
    if request.user.last_name==settings.COMPANY_MESSAGE:
        try:
            p=CompanyProfile.objects.get(user=request.user)
        except:
            return HttpResponse("Profile not found")
    else:
        try:
            p=StudentProfile.objects.get(user=request.user)
        except:
            return HttpResponse("Profile not found")
    if p.account_banned_permanent:
        return HttpResponse("Account has been permanently")
    if p.account_banned_temporary:
        return HttpResponse("Account has been for a short span of time, suggested to login again")
    if p.profile_filled==False and id==1:
        return redirect('profile')
        pass    
    return False

def profile(request):
    if error_detection(request,2)==False:
        return render(request,'dashboard/profile.html',context={})
    return error_detection(request,2)