from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import (login,authenticate,logout)
from django.conf import settings
from django.core.mail import send_mail
import math,random,string,datetime
from twilio.rest import Client
from home.models import CompanyProfile,StudentProfile
from .forms import StudentPhotoForm,StudentCVForm,CompanyAnnouncementForm
from .models import StaffPermissions, CompanyAnnouncement, Result

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
            cgpa=request.POST.get('cgpa')
            try:
                p=StudentProfile.objects.get(user=request.user)
                p.complete_address=address
                if str(gender)=='1':
                    p.gender='Male'
                elif str(gender)=='2':
                    p.gender='Female'
                else:
                    p.gender='Transgender'
                p.cgpa=float(cgpa)
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

def new_announcement_round(request):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        if request.method == "POST":
            internship_round=int(request.POST.get('internship_round'))
            if(internship_round>1):
                prev_round_for_result=request.POST.get('prev_round_for_result')
                if(Result.objects.filter(internship_round=prev_round_for_result, company=request.user).count()<=0):
                    return render(request, 'dashboard/new_round.html', context={"data": data, "error": "No result found with the given previous round number"})
            form = CompanyAnnouncementForm(request.POST,request.FILES)
            if form.is_valid():
                x=form.save()
                myid=x.id
                last_date_to_apply=request.POST.get('last_date_to_apply')
                com_ann=CompanyAnnouncement.objects.get(id=myid)
                com_ann.company=request.user
                if internship_round==1:
                    com_ann.first_round=True
                    com_ann.prev_round_for_result=0
                com_ann.last_date_to_apply=datetime.datetime.strptime(str(last_date_to_apply), '%Y-%m-%dT%H:%M')
                com_ann.save()
                return redirect('new_announcement_success', '1')
            else:
                return render(request, 'dashboard/new_round.html', context={"data": data, "error": form.errors})
        else:
            return render(request, 'dashboard/new_round.html', context={"data": data})
    return error_detection(request,1)
    
def new_announcement_success(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        else:
            data=get_my_profile(request)
            if item=='1':
                return render(request, 'dashboard/new_round.html', context={"data": data, "success": "Announcement Created"})
            if item=='2':
                return render(request, 'dashboard/new_announcement.html', context={"data": data, "success": "Announcement Created"})
            else:
                return HttpResponse("404: page not found")
    return error_detection(request,1)

def announcements(request):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        announcements=CompanyAnnouncement.objects.filter(company=request.user).order_by('announcement_date')
        return render(request, 'dashboard/announcements.html', context={"announcements": announcements})
    return error_detection(request,1)

def edit_announcement(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        if request.method=="POST":
            data=CompanyAnnouncement.objects.get(id=int(item))
            if data.company!=request.user:
                return HttpResponse("Announcement not found")
            internship_round=int(request.POST.get('internship_round'))
            if(internship_round>1 and data.general_announcement==False):
                prev_round_for_result=request.POST.get('prev_round_for_result')
                if(Result.objects.filter(internship_round=prev_round_for_result, company=request.user).count()<=0):
                    return render(request, 'dashboard/edit_announcements.html', context={"data": data, "error": "No result found with the given previous round number"})
            form = CompanyAnnouncementForm(request.POST,request.FILES)
            if form.is_valid():
                data.internship_round=form.cleaned_data['internship_round']
                data.round_name=form.cleaned_data['round_name']
                data.prev_round_for_result=form.cleaned_data['prev_round_for_result']
                data.message=form.cleaned_data['message']
                if form.cleaned_data['file']:
                    data.file=form.cleaned_data['file']
                if form.cleaned_data['file_for_prev_result']:
                    data.file_for_prev_result=form.cleaned_data['file_for_prev_result']
                last_date_to_apply=request.POST.get('last_date_to_apply')
                if data.internship_round==1:
                    data.first_round=True
                    data.prev_round_for_result=0
                if data.general_announcement==False:
                    data.last_date_to_apply=datetime.datetime.strptime(str(last_date_to_apply), '%Y-%m-%dT%H:%M')
                data.save()
                return redirect('edit_announcement', int(item))
            else:
                return render(request, 'dashboard/edit_announcements.html', context={"data": data, "error": form.errors})
                
        else:
            try:
                data=CompanyAnnouncement.objects.get(id=int(item))
                if data.company!=request.user:
                    return HttpResponse("Announcement not found")
            except:
                return HttpResponse("Announcement not found")
            return render(request, 'dashboard/edit_announcements.html', context={"data": data})
    return error_detection(request,1)

def new_announcement(request):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        if request.method == "POST":
            form = CompanyAnnouncementForm(request.POST,request.FILES)
            if form.is_valid():
                x=form.save()
                com_ann=CompanyAnnouncement.objects.get(id=x.id)
                com_ann.company=request.user
                com_ann.general_announcement=True
                com_ann.save()
                return redirect('new_announcement_success', '2')
            else:
                return render(request, 'dashboard/new_announcement.html', context={"data": data, "error": form.errors})
        else:
            return render(request, 'dashboard/new_announcement.html', context={"data": data})
    return error_detection(request,1)

def result(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        if request.method == "POST":
            pass
        else:
            data=CompanyAnnouncement.objects.get(id=int(item))
            if data.company!=request.user:
                return HttpResponse("Announcement not found")
            students=get_students(request, int(item))
            return render(request, 'dashboard/result.html', context={"data": data, "students": students})
    return error_detection(request,1)

#TO be COmpleted
def get_students(request, id_of_announcement):
    return 

def show_companies(request):
    if error_detection(request,1)==False:
        if request.user.is_staff or request.user.is_superuser or request.user.last_name==settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        eligible_companies_for_me=CompanyAnnouncement.objects.filter(general_announcement=False, first_round=True, last_date_to_apply__gte=datetime.datetime.now())
        copy=eligible_companies_for_me
        for each in copy:
            try:
                min_cgpa=CompanyProfile.objects.get(user=each.company).minimum_cgpa
                if data.cgpa<min_cgpa:
                    eligible_companies_for_me=eligible_companies_for_me.exclude(id=each.id)
            except:
                eligible_companies_for_me=eligible_companies_for_me.exclude(id=each.id)
        return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies_for_me})
    return error_detection(request,1)