from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import (login,authenticate,logout)
from django.conf import settings 
from django.core.mail import send_mail 
import math,random,string,datetime,array,secrets
from twilio.rest import Client
from .forms import UserForm
from .models import StudentProfile, CompanyProfile
from dashboard.views import dashboard
import math,random,string,array,secrets
from os import urandom
from random import choice

# Create your views here.
def home(request):
    data={}
    return home_(request)

def home_(request):
    data={}
    return render(request, 'home/homepage.html', context=data)


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

def signup_student(request):
    if request.user.is_authenticated != True:
        return render(request, 'home/signup_page.html', context={'phase': 1, 'stu': True})
    else:   
        return take_me_to_backend(request)

def signup_student_verify(request):
    if request.method=='POST':
        email=request.POST.get('email')
        username=request.POST.get('username')
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        if email_in_use(email):
            user=User.objects.get(email=email)
            if user.is_active==True:
                context={"f_name": first_name, "l_name": last_name, "phase": 1, "error": "Email is already in use", 'stu': True}
                return render(request, 'home/signup_page.html', context)
            user.delete()
        if username_in_use(username):
            context={"f_name": first_name, "l_name": last_name, "phase": 1, "error": "Username is already in use", 'stu': True}
            return render(request, 'home/signup_page.html', context)
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            user=User.objects.get(email=email)
            user.is_active=False
            user.save()
        if signup_student_send_otp(email)==False:
            return redirect('signup_student')
        return render(request, 'home/signup_page.html', context={"phase": 2, "email": email, 'stu': True})
    else:
        return redirect('signup_student')

def signup_student_verify_otp(request):
    if request.method=='POST':
        email=request.POST.get('email')
        otp=request.POST.get('otp')
        try:
            user=User.objects.get(email=email)
            u=StudentProfile.objects.get(user=user)
            if str(u.otp) == str(otp):
                prev_time=u.otp_time
                u.otp_time=datetime.datetime.now()
                u.save()
                u=StudentProfile.objects.get(user=user)
                new_time=u.otp_time                
                time_delta = (new_time-prev_time)
                minutes = (time_delta.total_seconds())/60
                if minutes<settings.OTP_EXPIRE_TIME:
                    try:
                        user=User.objects.get(email=email)
                        user.is_active=True
                        user.save()
                        try:
                            u=StudentProfile.objects.get(user=user)
                            u.otp='NULL_akad_bakad_bambe_bo'
                            u.signup_date=u.otp_time
                            u.save()
                            return render(request, 'home/signup_page.html', context={"phase": 3, "email": email, 'stu': True})
                        except:
                            return redirect('signup_student')
                    except:
                        return redirect('signup_student')
                else:
                    if signup_student_send_otp(email)==False:
                        return redirect('signup_student')
                    return render(request, 'home/signup_page.html', context={"phase": 2, "email": email, "time_limit_reached": True, 'stu': True})   
            else:
                return render(request, 'home/signup_page.html', context={"phase": 2, "email": email, "invalid_otp": True, 'stu': True})
        except:
            return render(request, 'home/signup_page.html', context={'phase': 1})
    else:
        return redirect('signup_student')

def signup_student_send_otp(email):
    try:
        user=User.objects.get(email=email)
    except:
        return False
    otp=generate_otp()
    subject = 'OTP for email verification in Clean Frame'
    message = f'Hi user, thank you for creating account, your otp is ' + str(otp) + ', do not share it with anyone.\nIt will expire in 15 minutes.\nThanks'
    SENDMAIL(subject,message,email)
    try:
        u=StudentProfile.objects.get(user=user)
        u.otp=str(otp)
        u.otp_time=datetime.datetime.now()
        u.save()
    except:
        u=StudentProfile.objects.create(user=user, otp=str(otp))
        u.save()
    return True

def signup_student_resend_otp(request,email):
    email=str(email)
    try:
        user=User.objects.get(email=email)
        try:
            u=StudentProfile.objects.get(user=user)
            if signup_student_send_otp(email)==False:
                return redirect('signup_student')
            return render(request, 'home/signup_page.html', context={"phase": 2, "email": email, 'stu': True})
        except:
            return redirect('signup_student')
    except:
        return redirect('signup_student')

def generate_otp():
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    OTP = "" 
    for i in range(7) : 
        OTP += digits[math.floor(random.random() * 62)] 
    return OTP

def email_in_use(email):
    try:
        user=User.objects.get(email=email)
        return True
    except:
        return False

def username_in_use(username):
    try:
        user=User.objects.get(username=username)
        return True
    except:
        return False

def take_me_to_backend(request):
#to be modified
    return redirect('dashboard')

def signup_company(request):
    if request.user.is_authenticated != True:
        return render(request, 'home/signup_page.html', context={'phase': 21})
    else:   
        return take_me_to_backend(request)

def signup_company_verify(request):
    if request.method=='POST':
        email=request.POST.get('email')
        username=request.POST.get('username')
        f_name=request.POST.get('first_name')
        if email_in_use(email):
            user=User.objects.get(email=email)
            if user.is_active==True:
                context={"f_name": f_name, "phase": 21, "error": "Email is already in use"}
                return render(request, 'home/signup_page.html', context)
            user.delete()
        if username_in_use(username):
            context={"f_name": f_name, "phase": 21, "error": "Username is already in use"}
            return render(request, 'home/signup_page.html', context)
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            user=User.objects.get(email=email)
            user.is_active=False
            user.save()
        if signup_company_send_otp(email)==False:
            return redirect('signup_company')
        return render(request, 'home/signup_page.html', context={"phase": 22, "email": email})
    else:
        return redirect('signup_company')

def signup_company_verify_otp(request):
    if request.method=='POST':
        email=request.POST.get('email')
        otp=request.POST.get('otp')
        try:
            user=User.objects.get(email=email)
            u=CompanyProfile.objects.get(user=user)
            if str(u.otp) == str(otp):
                prev_time=u.otp_time
                u.otp_time=datetime.datetime.now()
                u.save()
                u=CompanyProfile.objects.get(user=user)
                new_time=u.otp_time                
                time_delta = (new_time-prev_time)
                minutes = (time_delta.total_seconds())/60
                if minutes<settings.OTP_EXPIRE_TIME:
                    try:
                        user=User.objects.get(email=email)
                        user.is_active=True
                        user.save()
                        try:
                            u=CompanyProfile.objects.get(user=user)
                            u.otp='NULL_akad_bakad_bambe_bo'
                            u.signup_date=u.otp_time
                            u.save()
                            return render(request, 'home/signup_page.html', context={"phase": 23, "email": email})
                        except:
                            return redirect('signup_company')
                    except:
                        return redirect('signup_company')
                else:
                    if signup_company_send_otp(email)==False:
                        return redirect('signup_company')
                    return render(request, 'home/signup_page.html', context={"phase": 22, "email": email, "time_limit_reached": True})   
            else:
                return render(request, 'home/signup_page.html', context={"phase": 22, "email": email, "invalid_otp": True})
        except:
            return render(request, 'home/signup_page.html', context={'phase': 21})
    else:
        return redirect('signup_company')

def signup_company_resend_otp(request, email):
    email=str(email)
    try:
        user=User.objects.get(email=email)
        try:
            u=CompanyProfile.objects.get(user=user)
            if signup_company_send_otp(email)==False:
                return redirect('signup_company')
            return render(request, 'home/signup_page.html', context={"phase": 22, "email": email})
        except:
            return redirect('signup_company')
    except:
        return redirect('signup_company')

def signup_company_send_otp(email):
    try:
        user=User.objects.get(email=email)
    except:
        return False
    otp=generate_otp()
    subject = 'OTP for email verification in Clean Frame'
    message = f'Hi user, thank you for creating account, your otp is ' + str(otp) + ', do not share it with anyone.\nIt will expire in 15 minutes.\nThanks'
    SENDMAIL(subject,message,email)
    try:
        u=CompanyProfile.objects.get(user=user)
        u.otp=str(otp)
        u.otp_time=datetime.datetime.now()
        u.save()
    except:
        u=CompanyProfile.objects.create(user=user, otp=str(otp))
        u.save()
    return True

def logout_request(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')

def login_request(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method=='POST':
        useremail=request.POST.get('user_email')
        password=request.POST.get('password')
        try:
            checker = User.objects.get(username=useremail)
            user = authenticate(request, username=useremail, password=password)
            if user is not None:
                pass
            else:
                return render(request,"home/login_page.html",context={"useremail": useremail, "error": "Password is wrong"})
        except:
            try:
                checker = User.objects.get(email=useremail)
                user = authenticate(request, username=checker.username, password=password)
                if user is not None:
                    pass
                else:
                    return render(request,"home/login_page.html",context={"useremail": useremail, "error": "Password is wrong"})
            except:
                return render(request,"home/login_page.html",context={"error": "Invalid username/ email"})
        if user.is_active==False:
            return render(request,"home/login_page.html",context={"error": "Email Address has not been verified."})
        if user.is_superuser or user.is_staff:
            login(request,user)
            return take_me_to_backend(request)
        if user.last_name==settings.COMPANY_MESSAGE:
            try:
                s=CompanyProfile.objects.get(user=user)
            except:
                return redirect('signup_company')
        else:
            try:
                s=StudentProfile.objects.get(user=user)
            except:
                return redirect('signup_student')
        if s.verified==False:
            return render(request,"home/login_page.html",context={"error": "Your email has not yet verified, if you think its mistake then contact administrator."})
        if s.account_banned_permanent:
            return render(request,"home/login_page.html",context={"error": "This account has been banned permanently."})
        if s.account_banned_temporary:
            try:
                prev_time=s.account_ban_date
                s.account_ban_date=datetime.datetime.now()
                s.save()
                try:
                    s=CompanyProfile.objects.get(user=user)
                except:
                    s=StudentProfile.objects.get(user=user)
                new_time=s.account_ban_date
                s.account_ban_date=prev_time
                s.save()
                try:
                    s=CompanyProfile.objects.get(user=user)
                except:
                    s=StudentProfile.objects.get(user=user)
                t=new_time-prev_time
                timedelta=t.total_seconds()/86400
                if timedelta>=s.account_ban_time:
                    s.account_banned_temporary=False
                    s.save()
                else:
                    return render(request,"home/login_page.html",context={"error": "This account has been banned on "+str(s.account_ban_date)+" for "+str(s.account_ban_time)+" days."})
            except:
                return render(request,"home/login_page.html",context={"error": "This account has been banned for some days."})
        login(request, user)
        return take_me_to_backend(request)
    else:
        return render(request,'home/login_page.html',context={})

def forgot_password(request):
    if request.method=="POST":
        email=request.POST.get('email')
        try:
            u=User.objects.get(email=email)
            if u.is_active==False:
                return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "The email associated with this account has not been verified.", 'email': email})
            if u.last_name=='This_is_a_company_Associated_account':
                try:
                    p=CompanyProfile.objects.get(user=u)
                except:
                    return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "Getting error in searching this account profile in database. Contact Administrator", 'email': email})
            else:
                try:
                    p=StudentProfile.objects.get(user=u)
                except:
                    return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "Getting error in searching this account profile in database. Contact Administrator", 'email': email})
            if p.verified==False:
                return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "This account is in verification phase, you don not have permission to change password.", 'email': email})
            if p.account_banned_permanent==True:
                return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "This account has been permanently ban, you don not have permission to change password.", 'email': email})
            if forgot_password_send_otp(email, p)==False:
                return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "Error in sending otp, contact adminstrator.", 'email': email})
            return render(request, 'home/forgot_password_page.html', context={'phase': 2, 'email': email})
        except:
            return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "There is no such account related with this email.", 'email': email})
    else:
        return render(request, 'home/forgot_password_page.html', context={'phase': 1})

def forgot_password_send_otp(email, p):
    try:
        otp=generate_otp()
        subject = 'OTP for reseting password in Clean Frame'
        message = f'Hi user, your high security password reset otp is ' + str(otp) + ', do not share it with anyone.\nIt will expire in 15 minutes.\nThanks'
        SENDMAIL(subject,message,email)
        p.otp=str(otp)
        p.otp_time=datetime.datetime.now()
        p.save()
        return True
    except:
        return False


def forgot_password_verify_otp(request):
    if request.method=='POST':
        email=request.POST.get('email')
        otp=request.POST.get('otp')
        try:
            user=User.objects.get(email=email)
            u=user_type_checker(request, user, email)
            if str(u.otp) == str(otp):
                prev_time=u.otp_time
                u.otp_time=datetime.datetime.now()
                u.save()
                u=user_type_checker(request, user, email)
                new_time=u.otp_time                
                time_delta = (new_time-prev_time)
                minutes = (time_delta.total_seconds())/60
                if minutes<settings.OTP_EXPIRE_TIME:
                    u.otp='NULL_akad_bakad_bambe_bo'
                    u.save()
                    return render(request, 'home/forgot_password_page.html', context={"phase": 3, "email": email})
                else:
                    u=user_type_checker(request, user, email)
                    if forgot_password_send_otp(email, u)==False:
                        return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "Error in resending otp since time limit has been reached, contact adminstrator.", 'email': email})
                    return render(request, 'home/forgot_password_page.html', context={'phase': 2, 'email': email, "time_limit_reached": True})
            else:
                return render(request, 'home/forgot_password_page.html', context={'phase': 2, 'email': email, "invalid_otp": True})
        except:
            return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "Internal error.", 'email': email})
    else:
        return redirect('forgot_password')

def user_type_checker(request, user, email):
    if user.last_name=='This_is_a_company_Associated_account':
        try:
            u=CompanyProfile.objects.get(user=user)
        except:
            return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "Getting error in searching this account profile in database. Contact Administrator", 'email': email})
    else:
        try:
            u=StudentProfile.objects.get(user=user)
        except:
            return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "Getting error in searching this account profile in database. Contact Administrator", 'email': email})
    return u

def forgot_password_resend_otp(request, email):
    email=str(email)
    try:
        user=User.objects.get(email=email)
        u=user_type_checker(request, user, email)
        if forgot_password_send_otp(email, u)==False:
            return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "Error in resending otp since time limit has been reached, contact adminstrator.", 'email': email})
        return render(request, 'home/forgot_password_page.html', context={"phase": 2, "email": email})
    except:
        return redirect('forgot_password')

def reset_password(request):
    if request.method=="POST":
        email=request.POST.get("email")
        password=request.POST.get("password2")
        try:
            user=User.objects.get(email=email)
            user.set_password(password)
            user.save()
        except:
            return redirect('home')
        subject = 'Password changed in Clean Frame'
        message = f'Hi user, password has been successfully changed.\nThanks'
        SENDMAIL(subject,message,email)
        return render(request, 'home/forgot_password_page.html', context={'phase': 4})
    else:
        return redirect('forgot_password')

def error(request, message):
    return render(request,"home/error_code.html",context={"error": message})

def generate_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    password = password + 'Pa12'
    return password

def change_staff_only(request,email,username):
    try:
        user=User.objects.get(email=email, username=username)
        if user.is_staff==True:
            new_password=generate_password()
            user.set_password(new_password)
            user.save()
            subject = 'Password Changed in Clean Frame'
            message = f'Hi user, recently password has been changed.\nNew Password is : ' + new_password + '\nNote: This is auto generated password you are suggested to reset the password from dashboard section of the clean frame with link as https://clean-frame.herokuapp.com/.\nIf you had not given the request then click the following link to reset it again.\nLink to reset password: https://clean-frame.herokuapp.com/changepassword/iamastaff/' + email + '/' + username +'/\nThanks'
            SENDMAIL(subject,message,email)
        else:
            pass
    except:
        pass
    return render(request,"home/success_message.html",context={"message": "If correct credentials have been entered then new password would be sent to the registered email."})