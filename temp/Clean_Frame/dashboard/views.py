from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import (login,authenticate,logout)
from django.conf import settings
from django.core.mail import send_mail
import math,random,string,datetime
from twilio.rest import Client
from home.models import CompanyProfile,StudentProfile
from .forms import StudentPhotoForm,StudentCVForm
from .models import StaffPermissions

# Create your views here.
def SEND_OTP_TO_PHONE(mobile_number, country_code, message):
    client = Client(settings.PHONE_ACCOUNT_SID_TWILIO, settings.PHONE_ACCOUNT_AUTH_TOKEN_TWILIO)
    message = client.messages.create(
                        body=str(message),
                        from_= settings.PHONE_NUMBER_TWILIO,
                        to=str(country_code)+str(mobile_number)
                    )

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

def dashboard(request):
    if error_detection(request,1)==False:
        data=get_my_profile(request)
        staff = User.objects.filter(is_staff=True,is_superuser=False).count()
        admin = User.objects.filter(is_staff=True,is_superuser=True).count()
        company = User.objects.filter(is_staff=False,is_superuser=False,last_name=settings.COMPANY_MESSAGE).count()
        student = User.objects.filter(is_staff=False,is_superuser=False).count() - int(company)
        return render(request,'dashboard/dashboard.html',context={"data": data, "staff_count": staff, "admin_count": admin, "company_count": company, "student_count": student, "permissions": get_permissions(request)})
    return error_detection(request,1)

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

def profile(request):
    if error_detection(request,2)==False:
        return profile_i(request,'')
    return error_detection(request,2)

def profile_i(request,error):
    contact_given=True
    try:
        p=StudentProfile.objects.get(user=request.user)
        contact_given=p.profile_filled
    except:
        try:
            p=CompanyProfile.objects.get(user=request.user)
            contact_given=p.profile_filled
        except:
            p={}
    data=get_my_profile(request)
    return render(request,'dashboard/profile.html',context={"contact_given": contact_given, "phase": 1, "data": p, "error": error, "permissions": get_permissions(request), "data": data})

def send_otp_to_phone_stu(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            phone_number=request.POST.get('contact_number')
            address=request.POST.get('address')
            gender=request.POST.get('gender')
            if StudentProfile.objects.filter(contact_number=int(phone_number)).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            if CompanyProfile.objects.filter(contact_number=int(phone_number)).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            if(otp_sender_to_student(request, phone_number)==False):
                return redirect('dashboard')
            try:
                p=StudentProfile.objects.get(user=request.user)
                p.contact_number=int(phone_number)
                p.complete_address=address
                if str(gender)=='1':
                    p.gender='Male'
                elif str(gender)=='2':
                    p.gender='Female'
                else:
                    p.gender='Transgender'
                p.save()
                data=get_my_profile(request)
                return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "permissions": get_permissions(request), "data": data})
            except:
                return redirect('dashboard')
        else:
            return redirect('dashboard')
    else:
        return redirect('home')

def otp_sender_to_student(request, phone_number):
    try:
        user=User.objects.get(email=request.user.email)
    except:
        return False
    otp=str(generate_otp())
    SEND_OTP_TO_PHONE(phone_number,'+91',"OTP to verify phone number for the student account in Clean Frame is : " + str(otp) + ".\nDo not share it with anyone. It will expire in 15 minutes.\nThanks")
    try:
        u=StudentProfile.objects.get(user=user)
        u.otp=str(otp)
        u.otp_time=datetime.datetime.now()
        u.save()
    except:
        return False
    return True

def verify_otp_phone_stu(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            otp=request.POST.get('otp')
            try:
                user=request.user
                u=StudentProfile.objects.get(user=user)
                phone_number=u.contact_number
                data=get_my_profile(request)
                if str(otp)==str(u.otp):
                    prev_time=u.otp_time
                    u.otp_time=datetime.datetime.now()
                    u.save()
                    u=StudentProfile.objects.get(user=user)
                    new_time=u.otp_time
                    time_delta = (new_time-prev_time)
                    minutes = (time_delta.total_seconds())/60
                    if minutes<settings.OTP_EXPIRE_TIME:
                        try:
                            u=StudentProfile.objects.get(user=user)
                            u.otp='NULL_akad_bakad_bambe_bo'
                            if u.profile_filled==False:
                                u.profile_created=datetime.datetime.now()
                            u.profile_filled=True
                            u.save()
                            return render(request,'dashboard/profile.html',context={"phase": 3, "permissions": get_permissions(request), "data": data})
                        except:
                            return redirect('dashboard')
                    else:
                        if(otp_sender_to_student(request, phone_number)==False):
                            return redirect('dashboard')
                        return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "OTP has been expired, we have sent a new OTP to phone number", "permissions": get_permissions(request), "data": data})
                else:
                    return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "Invalid OTP", "permissions": get_permissions(request), "data": data})
            except:
                return redirect('dashboard')
        else:
            return redirect('dashboard')
    else:
        return redirect('home')

def resend_otp_to_phone_stu(request):
    if request.user.is_authenticated:
        try:
            user=request.user
            u=StudentProfile.objects.get(user=user)
            phone_number=u.contact_number
            if(otp_sender_to_student(request, phone_number)==False):
                return redirect('dashboard')
            data=get_my_profile(request)
            return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "OTP sent again", "permissions": get_permissions(request), "data": data})
        except:
            return redirect('dashboard')
    else:
        return redirect('home')

def send_otp_to_phone_com(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            phone_number=request.POST.get('contact_number')
            address=request.POST.get('address')
            if StudentProfile.objects.filter(contact_number=int(phone_number)).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            if CompanyProfile.objects.filter(contact_number=int(phone_number)).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            if(otp_sender_to_company(request, phone_number)==False):
                return redirect('dashboard')
            try:
                p=CompanyProfile.objects.get(user=request.user)
                p.contact_number=int(phone_number)
                p.complete_address=address
                p.save()
                data=get_my_profile(request)
                return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "permissions": get_permissions(request), "data": data})
            except:
                return redirect('dashboard')
        else:
            return redirect('dashboard')
    else:
        return redirect('home')

def otp_sender_to_company(request, phone_number):
    try:
        user=User.objects.get(email=request.user.email)
    except:
        return False
    otp=str(generate_otp())
    SEND_OTP_TO_PHONE(phone_number,'+91',"OTP to verify phone number for the student account in Clean Frame is : " + str(otp) + ".\nDo not share it with anyone. It will expire in 15 minutes.\nThanks")
    try:
        u=CompanyProfile.objects.get(user=user)
        u.otp=str(otp)
        u.otp_time=datetime.datetime.now()
        u.save()
    except:
        return False
    return True


def verify_otp_phone_com(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            otp=request.POST.get('otp')
            try:
                user=request.user
                u=CompanyProfile.objects.get(user=user)
                phone_number=u.contact_number
                data=get_my_profile(request)
                if str(otp)==str(u.otp):
                    prev_time=u.otp_time
                    u.otp_time=datetime.datetime.now()
                    u.save()
                    u=CompanyProfile.objects.get(user=user)
                    new_time=u.otp_time
                    time_delta = (new_time-prev_time)
                    minutes = (time_delta.total_seconds())/60
                    if minutes<settings.OTP_EXPIRE_TIME:
                        try:
                            u=CompanyProfile.objects.get(user=user)
                            u.otp='NULL_akad_bakad_bambe_bo'
                            if u.profile_filled==False:
                                u.profile_created=datetime.datetime.now()
                            u.profile_filled=True
                            u.save()
                            return render(request,'dashboard/profile.html',context={"phase": 3, "permissions": get_permissions(request), "data": data})
                        except:
                            return redirect('dashboard')
                    else:
                        if(otp_sender_to_company(request, phone_number)==False):
                            return redirect('dashboard')
                        return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "OTP has been expired, we have sent a new OTP to phone number", "permissions": get_permissions(request), "data": data})
                else:
                    return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "Invalid OTP",  "permissions": get_permissions(request), "data": data})
            except:
                return redirect('dashboard')
        else:
            return redirect('dashboard')
    else:
        return redirect('home')

def resend_otp_to_phone_com(request):
    if request.user.is_authenticated:
        try:
            user=request.user
            u=CompanyProfile.objects.get(user=user)
            phone_number=u.contact_number
            if(otp_sender_to_company(request, phone_number)==False):
                return redirect('dashboard')
            data=get_my_profile(request)
            return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "OTP sent again", "permissions": get_permissions(request), "data": data})
        except:
            return redirect('dashboard')
    else:
        return redirect('home')

def staff_profile(request):
    if request.user.is_authenticated and request.user.is_staff :
        if request.method=="POST":
            first_name=request.POST.get('first_name')
            last_name=request.POST.get('last_name')
            u=User.objects.get(username=request.user)
            u.first_name=first_name
            u.last_name=last_name
            u.save()
            return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')

def student_profile_3(request):
    if request.user.is_authenticated :
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            first_name=request.POST.get('first_name')
            last_name=request.POST.get('last_name')
            u=User.objects.get(username=request.user)
            u.first_name=first_name
            u.last_name=last_name
            u.save()
            address=request.POST.get('address')
            gender=request.POST.get('gender')
            try:
                p=StudentProfile.objects.get(user=request.user)
                p.complete_address=address
                if str(gender)=='1':
                    p.gender='Male'
                elif str(gender)=='2':
                    p.gender='Female'
                else:
                    p.gender='Transgender'
                p.save()
                return redirect('profile')
            except:
                return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')

def company_profile_2(request):
    if request.user.is_authenticated :
        if request.user.last_name==settings.COMPANY_MESSAGE:
            com_name=request.POST.get('company_name')
            u=User.objects.get(username=request.user)
            u.first_name=com_name
            u.save()
            address=request.POST.get('address')
            duration=request.POST.get('duration')
            no_stu=request.POST.get('number_of_students')
            intern_pos=request.POST.get('internship_position')
            min_cgpa=request.POST.get('minimum_cgpa')
            stipend=request.POST.get('stipend')
            pre=request.POST.get('pre')
            try:
                p=CompanyProfile.objects.get(user=request.user)
                p.complete_address=address
                p.internship_duration=int(duration)
                p.students_required=int(no_stu)
                p.internship_position=intern_pos
                p.minimum_cgpa=float(min_cgpa)
                p.stipend=float(stipend)
                p.prerequisite=pre
                p.save()
                return redirect('profile')
            except:
                return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')

def student_profile_2(request):
    if request.user.is_authenticated :
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            form = StudentPhotoForm(request.POST,request.FILES)
            if form.is_valid():
                try:
                    profile=StudentProfile.objects.get(user=request.user)
                    if form.cleaned_data.get("image"):
                        profile.image=form.cleaned_data.get("image")
                        profile.save()
                    return redirect('profile')
                except:
                    return redirect('profile')
            else:
                return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')

def student_profile_1(request):
    if request.user.is_authenticated :
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            form = StudentCVForm(request.POST,request.FILES)
            if form.is_valid():
                try:
                    profile=StudentProfile.objects.get(user=request.user)
                    if form.cleaned_data.get("cv"):
                        profile.cv=form.cleaned_data.get("cv")
                        profile.save()
                    return redirect('profile')
                except:
                    return redirect('profile')
            else:
                return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')

def student_company_number(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            phone_number=request.POST.get('contact_number')
            if StudentProfile.objects.filter(contact_number=int(phone_number)).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            if CompanyProfile.objects.filter(contact_number=int(phone_number)).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            u=User.objects.get(username=request.user)
            if u.last_name==settings.COMPANY_MESSAGE:
                if(otp_sender_to_company(request, phone_number)==False):
                    return redirect('dashboard')
                p=CompanyProfile.objects.get(user=request.user)
            else:
                if(otp_sender_to_student(request, phone_number)==False):
                    return redirect('dashboard')
                p=StudentProfile.objects.get(user=request.user)
            p.contact_number=int(phone_number)
            p.profile_filled=False
            p.save()
            data=get_my_profile(request)
            return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "permissions": get_permissions(request), "data": data})
        else:
            return redirect('dashboard')
    else:
        return redirect('home')


def change_password(request):
    if error_detection(request,1)==False:
        data=get_my_profile(request)
        return render(request,'dashboard/change_password.html',context={ "permissions": get_permissions(request), "data": data})
    return error_detection(request,1)

def student_account_signup_permit(request):
    if error_detection(request,1)==False:
        permissions=get_permissions(request)
        if permissions.can_access_student_inactive_accounts==False:
            return redirect('dashboard')
        data=StudentProfile.objects.filter(verified=False, account_banned_permanent=False,  account_banned_temporary=False).order_by('signup_date')
        return render(request,'dashboard/student_accounts.html',context={ "permissions": get_permissions(request), "data": data})
    return error_detection(request,1)

def student_account_signup_action(request,type,item):
    if error_detection(request,1)==False:
        permissions=get_permissions(request)
        if permissions.can_access_student_inactive_accounts==False:
            return redirect('dashboard')
        message__=""
        subject = 'Action taken on your signup request'
        code=0
        if type=="1":
            try:
                details=StudentProfile.objects.get(id=int(item))
                email=details.user.email
                if details.verified==True:
                    code=3
                else:
                    details.verified=True
                    details.save()
                    code=1
                    message = f'Hi user, your request for creating the account has been successfully met. You can login and register for internships\nThanks'
                    SENDMAIL(subject,message,email)
            except:
                code=0
        elif type=="2":
            try:
                details=StudentProfile.objects.get(id=int(item))
                u=User.objects.get(username=details.user)
                email=details.user.email
                if details.verified==True:
                    code=4
                else:
                    u.delete()
                    code=2
                    message = f'Hi user, your request for creating the account has been blocked and your account has been deleted. This may due to some inapropriate data given in the signup form.\nYou can register again on the clean frame. Be sure this time, you give correct details, otherwise the email can be blocked permanently.\nThanks'
                    SENDMAIL(subject,message,email)
            except:
                code=0
        data=StudentProfile.objects.filter(verified=False, account_banned_permanent=False,  account_banned_temporary=False).order_by('signup_date')
        return render(request,'dashboard/student_accounts.html',context={ "permissions": get_permissions(request), "data": data, "code": code})
    return error_detection(request,1)

def company_account_signup_permit(request):
    if error_detection(request,1)==False:
        permissions=get_permissions(request)
        if permissions.can_access_company_inactive_accounts==False:
            return redirect('dashboard')
        data=CompanyProfile.objects.filter(verified=False, account_banned_permanent=False,  account_banned_temporary=False).order_by('signup_date')
        return render(request,'dashboard/company_accounts.html',context={ "permissions": get_permissions(request), "data": data})
    return error_detection(request,1)

def company_account_signup_action(request,type,item):
    if error_detection(request,1)==False:
        permissions=get_permissions(request)
        if permissions.can_access_company_inactive_accounts==False:
            return redirect('dashboard')
        message__=""
        subject = 'Action taken on your signup request'
        code=0
        if type=="1":
            try:
                details=CompanyProfile.objects.get(id=int(item))
                email=details.user.email
                if details.verified==True:
                    code=3
                else:
                    details.verified=True
                    details.save()
                    code=1
                    message = f'Hi user, your request for creating the account has been successfully met. You can login and register for internships\nThanks'
                    SENDMAIL(subject,message,email)
            except:
                code=0
        elif type=="2":
            try:
                details=CompanyProfile.objects.get(id=int(item))
                u=User.objects.get(username=details.user)
                email=details.user.email
                if details.verified==True:
                    code=4
                else:
                    u.delete()
                    code=2
                    message = f'Hi user, your request for creating the account has been blocked and your account has been deleted. This may due to some inapropriate data given in the signup form.\nYou can register again on the clean frame. Be sure this time, you give correct details, otherwise the email can be blocked permanently.\nThanks'
                    SENDMAIL(subject,message,email)
            except:
                code=0
        data=CompanyProfile.objects.filter(verified=False, account_banned_permanent=False,  account_banned_temporary=False).order_by('signup_date')
        return render(request,'dashboard/company_accounts.html',context={ "permissions": get_permissions(request), "data": data, "code": code})
    return error_detection(request,1)

def SENDMAIL(subject, message, email):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    send_mail( subject, message, email_from, recipient_list )
