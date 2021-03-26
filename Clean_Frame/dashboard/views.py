from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import (login,authenticate,logout)
from django.conf import settings
from django.core.mail import send_mail
import math,random,string,datetime
from twilio.rest import Client
from home.models import *
from .forms import *
from .models import *
from threading import *


class Email_thread(Thread):
    def __init__(self,subject,message,email):
        self.email=email
        self.subject=subject
        self.message=message
        Thread.__init__(self)

    def run(self):
        SENDMAIL(self.subject,self.message,self.email)
        
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

def get_the_profile(user):
    data={}
    try:
        data=StudentProfile.objects.get(user=user)
    except:
        try:
            data=CompanyProfile.objects.get(user=user)
        except:
            data={}
    return data

def dashboard(request):
    if error_detection(request,1)==False:
        data=get_my_profile(request)
        if request.user.is_staff:
            staff = User.objects.filter(is_staff=True,is_superuser=False).count()
            admin = User.objects.filter(is_staff=True,is_superuser=True).count()
            company = User.objects.filter(is_staff=False,is_superuser=False,last_name=settings.COMPANY_MESSAGE).count()
            student = User.objects.filter(is_staff=False,is_superuser=False).count() - int(company)
            students_with_internship=StudentProfile.objects.filter(got_internship=True).count()
            return render(request,'dashboard1/dashboard_staff.html',context={"data": data, "staff_count": staff, "admin_count": admin, "company_count": company, "student_count": student, "permissions": get_permissions(request), "students_with_internship": students_with_internship})
        if request.user.last_name==settings.COMPANY_MESSAGE:
            internships_with_result=Internship.objects.filter(company=request.user, result_announced=True).count()
            internships_without_result=Internship.objects.filter(company=request.user, result_announced=False).count()
            internships=Internship.objects.filter(company=request.user)
            registrations=0
            for each in internships:
                registrations+=StudentRegistration.objects.filter(company__internship=each).count()
            selected_students=InternshipFinalResult.objects.filter(company=request.user,student_agrees=True).count()
            unselected_students=registrations-selected_students
            return render(request,'dashboard1/dashboard_company.html',context={"data": data, "internships_with_result": internships_with_result, "internships_without_result": internships_without_result, "selected_students": selected_students, "unselected_students": unselected_students, "internships": internships.count(), "registrations": registrations})
        else:
            return HttpResponse("Student Account")
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
            try:
                p=CompanyProfile.objects.get(user=request.user)
                p.complete_address=address
                p.save()
                return redirect('profile')
            except:
                return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')
    
def company_profile_3(request):
    if request.user.is_authenticated :
        if request.user.last_name==settings.COMPANY_MESSAGE:
            form = CompanyPhotoForm(request.POST,request.FILES)
            if form.is_valid():
                try:
                    profile=CompanyProfile.objects.get(user=request.user)
                    image=request.POST.get("image")
                    if image!="":
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

def student_profile_2(request):
    if request.user.is_authenticated :
        if request.user.last_name!=settings.COMPANY_MESSAGE or user_profile.is_staff or user_profile.is_superuser:
            form = StudentPhotoForm(request.POST,request.FILES)
            if form.is_valid():
                try:
                    profile=StudentProfile.objects.get(user=request.user)
                    image=request.POST.get("image")
                    if image!="":
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
                    Email_thread(subject,message,email).start()
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
                    Email_thread(subject,message,email).start()
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
                    Email_thread(subject,message,email).start()
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
                    Email_thread(subject,message,email).start()
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
        internships=Internship.objects.filter(company=request.user)
        prev_round_for_result=0
        if request.method == "POST":
            internship_name=request.POST.get('internship_name')
            internship_round=int(request.POST.get('internship_round'))
            try:
                int_obj=Internship.objects.get(id=int(internship_name))
                CompanyAnnouncement.objects.get(company=request.user, internship_round=internship_round, internship=int_obj)
                return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "error": "This round has been already declared"})
            except:
                pass
            if(internship_round>1):
                prev_round_for_result=request.POST.get('prev_round_for_result')
                try:
                    c=CompanyAnnouncement.objects.get(company=request.user, internship_round=prev_round_for_result, internship=int_obj)
                except:
                    return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "error": "No announcement found with the given previous round number"})
                if c.last_round==True:
                    return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "error": "Final Round of this internship has been announced"})
                if(StudentRegistration.objects.filter(company=c, result_status=1).count()<=0):
                    return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "error": "No student found whose previous round was cleared"})
            form = CompanyAnnouncementForm(request.POST,request.FILES)
            if form.is_valid():
                x=form.save()
                myid=x.id
                last_date_to_apply=request.POST.get('last_date_to_apply')
                com_ann=CompanyAnnouncement.objects.get(id=myid)
                com_ann.company=request.user
                last_round=request.POST.get("last_round")
                if int(last_round)==2:
                    com_ann.last_round=True
                if internship_round==1:
                    com_ann.first_round=True
                    com_ann.prev_round_for_result=0
                if len(last_date_to_apply) > 1 :
                    com_ann.last_date_to_apply=datetime.datetime.strptime(str(last_date_to_apply), '%Y-%m-%dT%H:%M')
                com_ann.internship=Internship.objects.get(id=int(internship_name))
                com_ann.save()
                if internship_round!=1:
                    com_ann=CompanyAnnouncement.objects.get(id=myid)
                    prev_ann=CompanyAnnouncement.objects.get(company=request.user, internship_round=prev_round_for_result, internship=int_obj)
                    register_students_for_next_round(request, prev_ann, com_ann)
                    notify_other_students_for_rejection(request, prev_ann, com_ann)
                return redirect('new_announcement_success', '1')
            else:
                return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "error": form.errors})
        else:
            internships=Internship.objects.filter(company=request.user)
            return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "internships": internships})
    return error_detection(request,1)

def register_students_for_next_round(request, prev, new):
    get_students=StudentRegistration.objects.filter(company=prev, result_status=1)
    for each in get_students:
        each.company=new
        each.result_status=0
        each.save()
        subject = 'Registration for next Round'
        message = f'Hi user, you have been successfully registered for next round of internship.\nDetails of this round are as follows:\nCompany Name: '+str(each.company.company.first_name)+'\nInternship Name: '+str(each.company.internship.internship_name)+'\nRound Number: '+str(each.company.internship_round)+'\nThanks'
        email=each.student.email
        Email_thread(subject,message,email).start()

def notify_other_students_for_rejection(request, prev, new):
    get_students=StudentRegistration.objects.filter(company=prev, result_status=0)
    for each in get_students:
        each.result_status=2
        each.save()
        subject = 'Internship Round Result'
        message = f'Hi user, We feel apology telling you that you have been rejected in an internship round.\nDetails of this round are as follows:\nCompany Name: '+str(each.company.company.first_name)+'\nInternship Name: '+str(each.company.internship.internship_name)+'\nRound Number: '+str(each.company.internship_round)+'\nThanks'
        email=each.student.email
        Email_thread(subject,message,email).start()

def new_announcement_success(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        else:
            data=get_my_profile(request)
            internships=Internship.objects.filter(company=request.user)
            if item=='1':
                return render(request, 'dashboard/new_round.html', context={"data": data, "success": "Announcement Created", "internships": internships})
            if item=='2':
                return render(request, 'dashboard/new_announcement.html', context={"data": data, "success": "Announcement Created", "internships": internships})
            else:
                return HttpResponse("404: page not found")
    return error_detection(request,1)

def announce_internship(request):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        else:
            data=get_my_profile(request)
            if request.method=="POST":
                duration=request.POST.get('duration')
                no_stu=request.POST.get('number_of_students')
                intern_pos=request.POST.get('internship_position')
                min_cgpa=request.POST.get('minimum_cgpa')
                stipend=request.POST.get('stipend')
                pre=request.POST.get('pre')
                internship_name=request.POST.get('internship_name')
                try:
                    intern=Internship.objects.get(company=request.user, internship_name=internship_name, stipend=stipend, internship_duration=duration, students_required=no_stu, internship_position=intern_pos, minimum_cgpa=min_cgpa, prerequisite=pre)
                    return render(request, 'dashboard/new_internship.html', context={"data": data, "error": "Internship with same details already exists"})
                except:
                    Internship.objects.create(company=request.user, internship_name=internship_name, stipend=stipend, internship_duration=duration, students_required=no_stu, internship_position=intern_pos, minimum_cgpa=min_cgpa, prerequisite=pre)
                    return render(request, 'dashboard/new_internship.html', context={"data": data, "success": "Internship created with given details"})
            # GO FOR GET METHOD
            return render(request, 'dashboard/new_internship.html', context={"data": data})

    return error_detection(request,1)

def announcements(request):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        announcements=CompanyAnnouncement.objects.filter(company=request.user).order_by('announcement_date')
        return render(request, 'dashboard/announcements.html', context={"announcements": announcements})
    return error_detection(request,1)

def internships(request):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        internships=Internship.objects.filter(company=request.user)
        return render(request, 'dashboard/internships.html', context={"internships": internships})
    return error_detection(request,1)

def edit_internship(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        if request.method=="POST":
            try:
                data=Internship.objects.get(id=int(item))
                if data.company!=request.user:
                    return HttpResponse("Announcement not found")
                data.internship_name=request.POST.get('internship_name')
                data.internship_duration=int(request.POST.get('duration'))
                data.students_required=int(request.POST.get('number_of_students'))
                data.internship_position=request.POST.get('internship_position')
                data.minimum_cgpa=float(request.POST.get('minimum_cgpa'))
                data.stipend=float(request.POST.get('stipend'))
                data.prerequisite=request.POST.get('pre')
                data.save()
                return render(request, 'dashboard/edit_internships.html', context={"data": data, "success": "Internship Details Updated"})
            except:
                return HttpResponse("Error in details entered by you or Announcement not found")
        else:
            try:
                data=Internship.objects.get(id=int(item))
                if data.company!=request.user:
                    return HttpResponse("Internship not found")
            except:
                return HttpResponse("Internship not found")
            return render(request, 'dashboard/edit_internships.html', context={"data": data})
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
                if data.first_round==True:
                    last_date_to_apply=request.POST.get('last_date_to_apply')
                if data.general_announcement==False and data.first_round==True:
                    data.last_date_to_apply=datetime.datetime.strptime(str(last_date_to_apply), '%Y-%m-%dT%H:%M')
                if data.internship_round==1:
                    data.first_round=True
                    data.prev_round_for_result=0
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

def stu_result(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        if request.method == "POST":
            students=request.POST.get("students")
            if len(students)<=3:
                return redirect('stu_result', item)
            spliter=students.split('**')
            mylist=spliter[0].split(",")
            if int(spliter[1])==1:
                for each_id in mylist:
                    get_re=StudentRegistration.objects.get(student=int(each_id), company=int(item))
                    if get_re.result_status!=1:
                        get_re.result_status=1
                        get_re.save()
                        subject = 'Internship Round Cleared'
                        message = f'Hi user, We congratulate you for clearing the round in internship.\nDetails of cleared round are as follows:\nCompany Name: '+str(get_re.company.company.first_name)+'\nInternship Name: '+str(get_re.company.internship.internship_name)+'\nRound Number: '+str(get_re.company.internship_round)+'\nThanks'
                        email=get_re.student.email
                        Email_thread(subject,message,email).start()
                return redirect('stu_result', item)
            if int(spliter[1])==2:
                for each_id in mylist:
                    get_re=StudentRegistration.objects.get(student=int(each_id), company=int(item))
                    if get_re.result_status==0:
                        get_re.result_status=2
                        get_re.save()
                        subject = 'Internship Round Result'
                        message = f'Hi user, We feel apology telling you that you have been rejected in an internship round.\nDetails of this round are as follows:\nCompany Name: '+str(get_re.company.company.first_name)+'\nInternship Name: '+str(get_re.company.internship.internship_name)+'\nRound Number: '+str(get_re.company.internship_round)+'\nThanks'
                        email=get_re.student.email
                        Email_thread(subject,message,email).start()
                return redirect('stu_result', item)
            return HttpResponse("INVALID REQUEST")
        else:
            try:
                data=CompanyAnnouncement.objects.get(id=int(item))
            except:
                return HttpResponse("Announcement Not Found")
            if data.company!=request.user:
                return HttpResponse("Announcement not found")
            students=get_students(request, data)
            return render(request, 'dashboard/result.html', context={"data": data, "students": students})
    return error_detection(request,1)

def internship_result(request,item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        try:
            internship=Internship.objects.get(id=int(item))
        except:
            return HttpResponse("Result Not Found")
        if internship.company!=request.user:
            return HttpResponse("Announcement not found")
        students=InternshipFinalResult.objects.filter(internship=internship)
        data=get_my_profile(request)
        return render(request, 'dashboard/internship_result.html', context={"students": students})
    return error_detection(request,1)

#TO be COmpleted
def get_students(request, announcement):
    name=announcement.internship.internship_name
    round=announcement.internship_round
    get_stu=StudentRegistration.objects.filter(company__internship__internship_name=name)
    return get_stu

def show_companies(request):
    if error_detection(request,1)==False:
        if request.user.is_staff or request.user.is_superuser or request.user.last_name==settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        if data.got_internship==True:
            return HttpResponse("You can't register for internships this season because you alrady have one")
        eligible_companies=get_eligible_companies_for_me_round_one(request)
        return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies})
    return error_detection(request,1)

def show_company_round_details(request, item):
    if error_detection(request,1)==False:
        if request.user.is_staff or request.user.is_superuser or request.user.last_name==settings.COMPANY_MESSAGE:
            return redirect('home')
        try:
            data1_is=True
            data=CompanyAnnouncement.objects.get(id=int(item))
            try:
                data2_is=True
                company_data=CompanyProfile.objects.get(user=data.company)
            except:
                data2_is=False
                company_data={}
        except:
            data1_is=False
            data2_is=False
            data={}
            company_data={}
        return render(request, 'dashboard/show_company_details.html', context={"announcement_data": data, "company_data": company_data, "data1": data1_is, "data2": data2_is})
    return error_detection(request,1)

def register_student_first_round_only(request, item):
    if error_detection(request,1)==False:
        if request.user.is_staff or request.user.is_superuser or request.user.last_name==settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        if data.got_internship==True:
            return HttpResponse("You can't register for internships this season because you alrady have one")
        eligible_companies=get_eligible_companies_for_me_round_one(request)
        try:
            ann=CompanyAnnouncement.objects.get(id=int(item))
            s_data=StudentProfile.objects.get(user=request.user)
            c_data=CompanyProfile.objects.get(user=ann.company)
        except:
            return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "error": "Error in fetching your profile or announcement not found"})
        if ann.first_round==False:
            return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "error": "Announcement Round is not 1, contact staff to see into this matter."})
        if s_data.cgpa<ann.internship.minimum_cgpa:
            return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "error": "Your aren't eligible to register for this company since your CGPA does not met minimum CGPA set by the company"})
        try:
            StudentRegistration.objects.get(student=request.user, company=ann)
            return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "error": "You are Already registered"})
        except:
            try:
                ProfilePermissions.objects.get(user_who_can_see=ann.company,user_whose_to_see=request.user)
            except:
                ProfilePermissions.objects.create(user_who_can_see=ann.company,user_whose_to_see=request.user)
            StudentRegistration.objects.create(student=request.user, company=ann)
        data=get_my_profile(request)
        eligible_companies=get_eligible_companies_for_me_round_one(request)
        return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "success": True})
    return error_detection(request,1)

def get_eligible_companies_for_me_round_one(request):
    eligible_companies=CompanyAnnouncement.objects.filter(general_announcement=False, first_round=True, last_date_to_apply__gte=datetime.datetime.now())
    copy=eligible_companies
    data=get_my_profile(request)
    for each in copy:
        if each.last_round==True:
            if each.last_round_result_announced==True:
                eligible_companies=eligible_companies.exclude(id=each.id)
                continue
        try:
            min_cgpa=each.internship.minimum_cgpa
            if data.cgpa<min_cgpa:
                eligible_companies=eligible_companies.exclude(id=each.id)
            else:
                internship=each.internship
                all_ann=CompanyAnnouncement.objects.filter(internship=internship)
                for i in all_ann:
                    try:
                        sr=StudentRegistration.objects.get(student=request.user, company=i)
                        eligible_companies=eligible_companies.exclude(id=each.id)
                        break
                    except:
                        continue
        except:
            eligible_companies=eligible_companies.exclude(id=each.id)
        try:
            next_round=CompanyAnnouncement.objects.get(internship=each.internship, company=each.company, internship_round=2)
            eligible_companies=eligible_companies.exclude(id=each.id)
        except:
            pass
    return eligible_companies

def show_registrations(request):
    if error_detection(request,1)==False:
        if request.user.is_staff or request.user.is_superuser or request.user.last_name==settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        registrations=StudentRegistration.objects.filter(student=request.user)
        #Also get registrations of other rounds
        return render(request, "dashboard/registrations.html", context={"registrations": registrations})
    return error_detection(request,1)

def internship_action(request,item,type):
    if error_detection(request,1)==False:
        if request.user.is_staff or request.user.is_superuser or request.user.last_name==settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        try:
            registration=StudentRegistration.objects.get(id=int(item))
        except:
            return HttpResponse("Registration not found")
        if request.user!=registration.student:
            return HttpResponse("Registration not found")
        if registration.result_status!=1 or registration.internship_cleared==False:
            return HttpResponse("Error: may be this is not you are looking for.")
        try:
            company_announcement=registration.company
            internship=registration.company.internship
        except:
            return HttpResponse("Error: Internship not found")
        if company_announcement.last_round==False or company_announcement.last_round_result_announced==False:
            return HttpResponse("Error: Not a last round or final results have not been seized")
        if internship.result_announced==False:
            return HttpResponse("Error: Result of this internship has not been announced")
        try:
            internship_result=InternshipFinalResult.objects.filter(internship=internship, student=request.user)
        except:
            return HttpResponse("Error: Internship Result not found")
        if internship_result.count()!=1:
            return HttpResponse("Error: More than 1 resuls found for this, can\'t fetch which to take")
        if internship_result[0].student_agrees==0:
            if int(type)==2:
                result=internship_result[0]
                result.student_agrees=1
                result.save()
                registration.my_action=1
                registration.save()
                subject = 'Reverted Back'
                message = f'Hi user, you have reverted back your selection in the internship which can\'t be undone, you can try for another interships.\nDetails of this internship round are as follows:\nCompany Name: '+str(registration.company.company.first_name)+'\nInternship Name: '+str(registration.company.internship.internship_name)+'\nRound Number: '+str(registration.company.internship_round)+' (last Round)\nThanks'
                email=request.user.email
                Email_thread(subject,message,email).start()
                return redirect('show_registrations')
            elif int(type)==1:
                result=internship_result[0]
                result.student_agrees=2
                result.save()
                registration.my_action=2
                registration.save()
                subject = 'Congratulations! intern'
                message = f'Hi user, you have have been sucessfully selected for the internship, we congratulate for being an intern.\nNote: According to one student one company policy you can\'t regitser for other internships now\nDetails of this internship are as follows:\nCompany Name: '+str(registration.company.company.first_name)+'\nInternship Name: '+str(registration.company.internship.internship_name)+'\nThanks'
                email=request.user.email
                Email_thread(subject,message,email).start()
                my_registrations=StudentRegistration.objects.filter(student=request.user)
                my_registrations=my_registrations.exclude(id=int(item))
                for each in my_registrations:
                    each.result_status=3
                    each.save()
                profile=get_my_profile(request)
                profile.got_internship=True
                profile.save()
                return redirect('show_registrations')
            else:
                return HttpResponse("404 Error: Page not found")
        else:
            return HttpResponse("Error: You have already taken an action which can\'t be undone")
    return error_detection(request,1)

def delete_internship(request,item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        try:
            inter=Internship.objects.get(id=int(item))
            if inter.company==request.user:
                inter.delete()
                return redirect('internships')
            else:
                return HttpResponse("This account has no Permission to delete it")
        except:
            return HttpResponse("Internship Details not found")
    return error_detection(request,1)


def seeze_results(request,item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        try:
            comann=CompanyAnnouncement.objects.get(id=int(item))
            if comann.company!=request.user:
                return HttpResponse("Announcement Details not found")
            if comann.last_round==False:
                return HttpResponse("Not a last round")
            internship=comann.internship
            if internship.result_announced==True:
                return HttpResponse("Final Result has been announced")
            accept_discard_students(request,comann)
            return redirect('stu_result',item)
        except:
            return HttpResponse("Announcement Details not found")
    return error_detection(request,1)

def accept_discard_students(request,announcement):
    internship=announcement.internship
    company=request.user
    registrations=StudentRegistration.objects.filter(company=announcement)
    for each in registrations:
        if each.result_status==1:
            each.internship_cleared=True
            each.save()
            try:
                InternshipFinalResult.objects.get(internship=internship, company=company, student=each.student)
            except:
                InternshipFinalResult.objects.create(internship=internship, company=company, student=each.student)
            subject = 'Internship Selection Last Round'
            message = f'Hi user, you have been selected by the company in the last round of internship.\nDetails of the last cleared round are as follows:\nCompany Name: '+str(each.company.company.first_name)+'\nInternship Name: '+str(each.company.internship.internship_name)+'\nRound Number: '+str(each.company.internship_round)+' (Last Round) \nThanks'
            email=each.student.email
            Email_thread(subject,message,email).start()
        if each.result_status==0:
            each.result_status=2
            each.save()
            subject = 'Internship Result Last Round'
            message = f'Hi user, you have been rejected in the last round of internship, you can try for another interships.\nDetails of this round are as follows:\nCompany Name: '+str(each.company.company.first_name)+'\nInternship Name: '+str(each.company.internship.internship_name)+'\nRound Number: '+str(each.company.internship_round)+' (last Round)\nThanks'
            email=each.student.email
            Email_thread(subject,message,email).start()
    all_ann=CompanyAnnouncement.objects.filter(internship=internship, company=company)
    for each in all_ann:
        each.last_round_result_announced=True
        each.save()
    internship.result_announced=True
    internship.save()
            

def delete_announcement(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        try:
            comann=CompanyAnnouncement.objects.get(id=int(item))
            if comann.company!=request.user:
                return HttpResponse("Announcement Details not found")
            previous_round = comann.prev_round_for_result
            round_no=int(comann.internship_round)
            if comann.company==request.user:
                if round_no > 1:
                    try:
                        internship = comann.internship
                        abcd = CompanyAnnouncement.objects.filter(internship = internship)
                        mx=0
                        for each in abcd:
                            mx=get_max(int(mx),int(each.internship_round))
                        if mx==int(comann.internship_round):
                            set_results_for_previous_round(request, int(previous_round), int(comann.internship_round), comann.internship)
                    except:
                        pass
                comann.delete()
                return redirect('announcements')
            else:
                return HttpResponse("This account has no Permission to delete it")
        except:
            return HttpResponse("Announcement Details not found")
    return error_detection(request,1)

def set_results_for_previous_round(request, old, new, internship):
    students = StudentRegistration.objects.filter(company__internship = internship)
    while old > 0:
        try:
            old_announcement = CompanyAnnouncement.objects.get(internship = internship, internship_round = str(old))
            break
        except:
            old=old-1
    if old==0:
        return
    for each in students:
        if each.company.internship_round == str(new):
            each.result_status = 1
            each.company = old_announcement
            each.save()
            subject = 'Reverted back for previous Round'
            message = f'Hi user, you have been reverted back to previous round of internship because company deleted the latest round.\nDetails of the current cleared round are as follows:\nCompany Name: '+str(each.company.company.first_name)+'\nInternship Name: '+str(each.company.internship.internship_name)+'\nRound Number: '+str(each.company.internship_round)+'\nThanks'
            email=each.student.email
            Email_thread(subject,message,email).start()
            
            
def get_max(a,b):
    if a>b:
        return a
    return b
            
def check_student_profile(request, item):
    if error_detection(request,1)==False:
        try:
            user_profile=User.objects.get(id=int(item))
            data=get_passed_profile(user_profile)
            if data=={}:
                return HttpResponse("Profile Not Found")
        except:
            return HttpResponse("Profile Not Found")
        if user_profile.last_name==settings.COMPANY_MESSAGE or user_profile.is_staff or user_profile.is_superuser:
            return HttpResponse("Profile not found")
        
        if request.method=="POST":
            permission=int(request.POST.get('profile_visibility'))
            user_id=int(request.POST.get('user_id'))
            try:
                user=User.objects.get(id=user_id)
            except:
                return HttpResponse("User not found")
            if request.user!=user:
                return HttpResponse("User Profile is Hidden")
            try:
                per=ProfileVisibility.objects.get(user=request.user)
            except:
                per=ProfileVisibility.objects.create(user=request.user)
                per.save()
            per.to_registered_companies=False
            per.to_all_companies=False
            per.to_all_students=False
            per.to_all=False
            if permission==1:
                per.to_registered_companies=True
            elif permission==2:
                per.to_all_companies=True
            elif permission==3:
                per.to_all_students=True
            elif permission==4:
                per.to_all=True
            per.save()
            return redirect('check_student_profile',request.user.id)
        try:
            my_permissions=ProfileVisibility.objects.get(user=user_profile)
            if request.user.is_staff==False:
                if check_profilepage_permissions(request, item) == False:
                    return HttpResponse("You do not not permission to view this user's profile page")
        except:
            ProfileVisibility.objects.create(user=user_profile, to_all=True)
            my_permissions=ProfileVisibility.objects.get(user=user_profile)
        image=data.image
        return render(request,'dashboard/profile_page_student.html',context={"data": data, "image": image, "permissions": my_permissions})
    return error_detection(request,1)

def check_profilepage_permissions(request, item):
    try:
        user_profile=User.objects.get(id=int(item))
        my_permissions=ProfileVisibility.objects.get(user=user_profile)
    except:
        return False
    if request.user == user_profile:
        return True
    else:
        try:
            ProfilePermissions.objects.get(user_who_can_see=request.user,user_whose_to_see=user_profile)
            return True
        except:
            if my_permissions.to_all==True:
                return True
            if my_permissions.to_all_students==True:
                if request.user.last_name!=settings.COMPANY_MESSAGE:
                    return True
            if my_permissions.to_all_companies==True:
                if request.user.last_name==settings.COMPANY_MESSAGE:
                    return True
            return False
        
def check_company_profile(request, item):
    if error_detection(request,1)==False:
        try:
            user_profile=User.objects.get(id=int(item))
            data=get_passed_profile(user_profile)
            if data=={}:
                return HttpResponse("Profile Not Found")
        except:
            return HttpResponse("Profile Not Found")
        if user_profile.last_name!=settings.COMPANY_MESSAGE or user_profile.is_staff or user_profile.is_superuser:
            return HttpResponse("Profile not found")
        image=data.image
        return render(request,'dashboard/profile_page_company.html',context={"data": data, "image": image})
    return error_detection(request,1)

def check_staff_profile(request,item):
    if error_detection(request,1)==False:
        try:
            user_profile=User.objects.get(id=int(item))
        except:
            return HttpResponse("Profile Not Found")
        if request.user.is_staff==False:
            return HttpResponse("Profile not found")
        if request.user!=user_profile:
            return HttpResponse("Profile not found")
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
        except:
            StaffPermissions.objects.create(user=request.user)
            permissions=StaffPermissions.objects.get(user=request.user)
        return render(request,'dashboard/profile_page_staff.html',context={"permissions": permissions})
    return error_detection(request,1)

def get_passed_profile(user):
    data={}
    try:
        data=StudentProfile.objects.get(user=user)
    except:
        try:
            data=CompanyProfile.objects.get(user=user)
        except:
            data={}
    return data

def restrict_users(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_ban_users==False and permissions.can_delete_staff_accounts==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        normal_users={}
        if permissions.can_ban_users:
            normal_users=get_simple_users(request)
        staff_users={}
        if request.user.is_superuser and permissions.can_delete_staff_accounts:
            staff_users=User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
            staff_users=staff_users.exclude(id=request.user.id)
        return render(request,'dashboard1/ban_users.html',context={"normal_users": normal_users, "staff_users": staff_users, "permissions": permissions})
    return error_detection(request,1)

def get_simple_users(request):
    if request.user.is_staff==False:
        return HttpResponse("404: ERROR")
    users=User.objects.filter(is_staff=False, is_active=True, is_superuser=False)
    for each in users:
        profile=get_the_profile(each)
        if profile=={}:
            users=users.exclude(id=each.id)
        else:
            if profile.account_banned_permanent==True or profile.account_banned_temporary==True:
                users=users.exclude(id=each.id)
    return users

def ban_user_account_permanent(request,item):
    if error_detection(request,1)==False:
        if request.user.is_staff==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_ban_users==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        user_ban=User.objects.get(id=int(item))
        if user_ban.is_staff or user_ban.is_superuser:
            return redirect('restrict_users')
        profile=get_the_profile(user_ban)
        if profile=={}:
            return redirect('restrict_users')
        if profile.account_banned_permanent==True:
            return redirect('restrict_users')
        profile.account_banned_permanent=True
        profile.save()   
        subject = 'Account Seized'
        message = f'Hi user, your account has been banned permanently.\nAccount is banned by ' + request.user.email + ' , contact this email for any query.\nThanks'
        email=user_ban.email
        Email_thread(subject,message,email).start()
        normal_users={}
        if permissions.can_ban_users:
            normal_users=get_simple_users(request)
        staff_users={}
        if request.user.is_superuser and permissions.can_delete_staff_accounts:
            staff_users=User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
            staff_users=staff_users.exclude(id=request.user.id)
        return render(request,'dashboard1/ban_users.html',context={"normal_users": normal_users, "staff_users": staff_users, "permissions": permissions, "code": "1"})
    return error_detection(request,1)

def ban_user_account_temporary(request,item):
    if error_detection(request,1)==False:
        if request.user.is_staff==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_ban_users==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        user_ban=User.objects.get(id=int(item))
        if user_ban.is_staff or user_ban.is_superuser:
            return redirect('restrict_users')
        profile=get_the_profile(user_ban)
        if profile=={}:
            return redirect('restrict_users')
        if profile.account_banned_temporary==True:
            return redirect('restrict_users')
        ban_time=settings.TEMORARY_BAN_TIME
        profile.account_banned_temporary=True
        profile.account_ban_time=ban_time
        profile.account_ban_date=datetime.datetime.now()
        profile.save()   
        subject = 'Account Seized'
        message = f'Hi user, your account has been banned temporarily for ' + str(ban_time) + ' days.\nAccount is banned by ' + request.user.email + ' , contact this email for any query.\nThanks'
        email=user_ban.email
        Email_thread(subject,message,email).start()
        normal_users={}
        if permissions.can_ban_users:
            normal_users=get_simple_users(request)
        staff_users={}
        if request.user.is_superuser and permissions.can_delete_staff_accounts:
            staff_users=User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
            staff_users=staff_users.exclude(id=request.user.id)
        return render(request,'dashboard1/ban_users.html',context={"normal_users": normal_users, "staff_users": staff_users, "permissions": permissions, "code": "3"})
    return error_detection(request,1)

def delete_staff_account_admin(request,item,type):
    if error_detection(request,1)==False:
        if request.user.is_staff==False or request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_delete_staff_accounts==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        try:
            user_del=User.objects.get(id=int(item))
        except:
            return HttpResponse("User not Found")
        if user_del.is_superuser==True:
            return HttpResponse("Cannot delete this account")
        if user_del.is_staff==False:
            return HttpResponse("Cannot delete this account")
        email=user_del.email
        user_del.delete()   
        subject = 'Account Deleted'
        message = f'Hi user, your account has been deleted permanently.\nAccount is deleted by ' + request.user.email + ' , contact this email for any query.\nThanks'
        Email_thread(subject,message,email).start()
        if int(type)==1:
            normal_users={}
            if permissions.can_ban_users:
                normal_users=get_simple_users(request)
            staff_users={}
            if request.user.is_superuser and permissions.can_delete_staff_accounts:
                staff_users=User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
                staff_users=staff_users.exclude(id=request.user.id)
            return render(request,'dashboard1/ban_users.html',context={"normal_users": normal_users, "staff_users": staff_users, "permissions": permissions, "code": "2"})
        if int(type)==2:
            if request.user.is_superuser and permissions.can_manage_staff_accounts:
                users=User.objects.filter(is_staff=True, is_superuser=False)
            return render(request,'dashboard1/manage_staff_accounts.html',context={"permissions": permissions, "data": users, "message": "1 Staff Account deleted"})
    return error_detection(request,1)


def unban_user(request,item):
    if error_detection(request,1)==False:
        if request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_unban_users==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if int(item)==0:
            banned_users=get_banned_users(request)
            return render(request,'dashboard1/unban_users.html',context={"banned_users": banned_users, "permissions": permissions})

        try:
            user_unban=User.objects.get(id=int(item))
        except:
            return redirect('unban_user','0')
        if user_unban.is_superuser==True:
            return redirect('unban_user','0')
        if user_unban.is_staff==True:
            return redirect('unban_user','0')
        profile=get_the_profile(user_unban)
        if profile=={}:
            return redirect('unban_user','0')
        if profile.account_banned_temporary==True or profile.account_banned_permanent==True:
            profile.account_banned_temporary=False
            profile.account_banned_permanent=False
            profile.save()
            subject = 'Account Unbanned'
            message = f'Hi user, your account has been unbanned.\nAccount is unbanned by ' + request.user.email + ' , contact this email for any query.\nThanks'
            email=user_unban.email
            Email_thread(subject,message,email).start()
        banned_users=get_banned_users(request)
        return render(request,'dashboard1/unban_users.html',context={"banned_users": banned_users, "permissions": permissions, "success": True})
    return error_detection(request,1)


def get_banned_users(request):
    if request.user.is_superuser==False:
        return HttpResponse("404: ERROR PAGE NOT FOUND")
    users=User.objects.filter(is_staff=False, is_active=True, is_superuser=False)
    for each in users:
        profile=get_the_profile(each)
        if profile=={}:
            users=users.exclude(id=each.id)
        else:
            if profile.account_banned_permanent==False and profile.account_banned_temporary==False:
                users=users.exclude(id=each.id)
    return users

def create_company_account(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_create_new_company_account==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            username=request.POST.get('username')
            first_name=request.POST.get('first_name')
            email=request.POST.get('email')
            try:
                user=User.objects.get(email=email)
                return render(request,'dashboard1/new_company_account.html',context={"permissions": permissions, "error": "Account exists with given email", "username": username, "email": email, "first_name": first_name})
            except:
                try:
                    user=User.objects.get(username=username)
                    return render(request,'dashboard1/new_company_account.html',context={"permissions": permissions, "error": "Account exists with given username", "username": username, "email": email, "first_name": first_name})
                except:
                    pass
            user=User.objects.create(username=username, email=email, first_name=first_name, last_name=settings.COMPANY_MESSAGE)
            password=generate_random_password(20)
            user.set_password(password)
            user.save()
            profile=CompanyProfile.objects.create(user=user, verified=True)
            subject = 'Company Account created'
            message = f'Hi user, an account has been created for this email in Clean Frame.\nAccount Details are as follows:\nUsername: '+str(user)+'\nPassword: '+str(password)+'\nCompany Name: '+str(user.first_name)+'\nNow you can offer internships by fulfilling minimum profile details.\nThe password is a auto generated password so we suggest you to change it.\nThanks'
            email=email
            Email_thread(subject,message,email).start()
            return render(request,'dashboard1/new_company_account.html',context={"permissions": permissions, "success": "Company Account created succesfully"})
        else:
            return render(request,'dashboard1/new_company_account.html',context={"permissions": permissions})
    return error_detection(request,1)

def generate_random_password(n):
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@#$!"
    password = ""
    for i in range(n) :
        password += digits[math.floor(random.random() * 62)]
    password+='@'
    return password

def manage_blogs(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_blogs==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            pass
        else:
            blogs=Blog.objects.all()
            return render(request,'dashboard1/manage_blogs.html',context={"permissions": permissions, "blogs": blogs})
    return error_detection(request,1)

def create_new_blog(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_blogs==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            form=BlogForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                return redirect('manage_blogs')
            else:
                error=form.errors
                return render(request,'dashboard1/new_blog.html',context={"permissions": permissions, "error": error})
        else:
            return render(request,'dashboard1/new_blog.html',context={"permissions": permissions})
    return error_detection(request,1)

def delete_blog(request,item):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_blogs==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        try:
            Blog.objects.get(id=int(item)).delete()
        except:
            pass
        return redirect('manage_blogs')
    return error_detection(request,1)

def edit_blog(request,item):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_blogs==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        try:
            blog=Blog.objects.get(id=int(item))
        except:
            return HttpResponse("Blog not found")
        if request.method=="POST":
            form=BlogForm(request.POST,request.FILES)
            if form.is_valid():
                blog.title=form.cleaned_data['title']
                blog.short_description=form.cleaned_data['short_description']
                blog.brief_description=form.cleaned_data['brief_description']
                if form.cleaned_data['file'] != None:
                    blog.file=form.cleaned_data['file']
                blog.save()
                return redirect('manage_blogs')
            else:
                error=form.errors
                return render(request,'dashboard1/new_blog.html',context={"permissions": permissions, "error": error})
        else:
            return render(request,'dashboard1/edit_blog.html',context={"permissions": permissions, "data": blog})
    return error_detection(request,1)

def manage_staff_accounts(request):
    if error_detection(request,1)==False:
        if request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_staff_accounts==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            pass
        else:
            users=User.objects.filter(is_staff=True, is_superuser=False)
            return render(request,'dashboard1/manage_staff_accounts.html',context={"permissions": permissions, "data": users})
    return error_detection(request,1)

def edit_staff_permissions(request, item):
    if error_detection(request,1)==False:
        if request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_staff_accounts==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        try:
            staff_data=User.objects.get(id=int(item))
            try:
                data=StaffPermissions.objects.get(user=staff_data)
            except:
                StaffPermissions.objects.create(user=staff_data)
                data=StaffPermissions.objects.get(user=staff_data)
        except:
            return HttpResponse("Staff Not Found")
            
        if request.method=="POST":
            data.can_access_student_inactive_accounts=True if request.POST.get('can_access_student_inactive_accounts')=="1" else False
            data.can_access_company_inactive_accounts=True if request.POST.get('can_access_company_inactive_accounts')=="1" else False
            data.can_ban_users=True if request.POST.get('can_ban_users')=="1" else False
            data.can_create_new_company_account=True if request.POST.get('can_create_new_company_account')=="1" else False
            data.can_manage_blogs=True if request.POST.get('can_manage_blogs')=="1" else False
            data.can_manage_technical_support=True if request.POST.get('can_manage_technical_support')=="1" else False
            data.can_give_notifications=True if request.POST.get('can_give_notifications')=="1" else False
            data.save()
            return redirect('edit_staff_permissions',item)
        else:
            return render(request,'dashboard1/edit_staff_permissions.html',context={"permissions": permissions, "data": data, "staff_data": staff_data})
    return error_detection(request,1)

def create_new_staff_account(request):
    if error_detection(request,1)==False:
        if request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_staff_accounts==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')            
        if request.method=="POST":
            username=request.POST.get('username')
            first_name=request.POST.get('first_name')
            email=request.POST.get('email')
            try:
                user=User.objects.get(email=email)
                return render(request,'dashboard1/new_staff_account.html',context={"permissions": permissions, "error": "Account exists with given email", "username": username, "email": email, "first_name": first_name})
            except:
                try:
                    user=User.objects.get(username=username)
                    return render(request,'dashboard1/new_staff_account.html',context={"permissions": permissions, "error": "Account exists with given username", "username": username, "email": email, "first_name": first_name})
                except:
                    pass
            user=User.objects.create(username=username, email=email, first_name=first_name)
            password=generate_random_password(20)
            user.set_password(password)
            user.is_staff=True
            user.save()
            data=StaffPermissions.objects.create(user=user)
            subject = 'Staff Account created'
            message = f'Hi user, an staff account has been created for this email in Clean Frame.\nAccount Details are as follows:\nUsername: '+str(user)+'\nPassword: '+str(password)+'\nName: '+str(user.first_name)+'\nNow you are a staff, visit the website, login and see what permissions you have been provided with.\nThe password is a auto generated password so we suggest you to change it.\nThanks'
            email=email
            Email_thread(subject,message,email).start()
            data.can_access_student_inactive_accounts=True if request.POST.get('can_access_student_inactive_accounts')=="1" else False
            data.can_access_company_inactive_accounts=True if request.POST.get('can_access_company_inactive_accounts')=="1" else False
            data.can_ban_users=True if request.POST.get('can_ban_users')=="1" else False
            data.can_create_new_company_account=True if request.POST.get('can_create_new_company_account')=="1" else False
            data.can_manage_blogs=True if request.POST.get('can_manage_blogs')=="1" else False
            data.can_manage_technical_support=True if request.POST.get('can_manage_technical_support')=="1" else False
            data.can_give_notifications=True if request.POST.get('can_give_notifications')=="1" else False
            data.save()
            return redirect('manage_staff_accounts')
        else:
            return render(request,'dashboard1/new_staff_account.html',context={"permissions": permissions})
    return error_detection(request,1)

def notifications(request):
    if error_detection(request,1)==False:
        notifications=Notification.objects.filter(notification_receiver=request.user).order_by('-date')
        if notifications.count()==0:
            notifications="0"
        return render(request,'dashboard1/notifications.html',context={"notifications": notifications})
    return error_detection(request,1)

def give_notifications(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_give_notifications==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            message=request.POST.get("message")
            user_id=int(request.POST.get("user_id"))
            if user_id>0:
                try:
                    user=User.objects.get(id=int(user_id))
                except:
                    return HttpResponse("User not exists")
                Notification.objects.create(notification_sender=request.user, notification_receiver=user, notification=message)
            else:
                if user_id==-1:
                    users=User.objects.filter(is_staff=True, is_superuser=False)
                elif user_id==-2:
                    users=User.objects.filter(is_staff=False, is_superuser=False, last_name=settings.COMPANY_MESSAGE)
                elif user_id==-3:
                    users=User.objects.filter(is_staff=False, is_superuser=False).exclude(last_name=settings.COMPANY_MESSAGE)
                else:
                    return HttpResponse("URL NOT FOUND")
                for each in users:
                    Notification.objects.create(notification_sender=request.user, notification_receiver=each, notification=message)
            return redirect('give_notifications')
        else:
            data=User.objects.all()
            data=data.exclude(id=request.user.id)
            return render(request,'dashboard1/send_notifications.html',context={"permissions": permissions, "data": data})
    return error_detection(request,1)

def notification_delete(request, item):
    if error_detection(request,1)==False:
        try:
            notification=Notification.objects.get(id=int(item))
        except:
            return redirect('notifications')
        if notification.notification_receiver==request.user:
            notification.delete()
        return redirect('notifications')
    return error_detection(request,1)

def technical_support(request):
    if error_detection(request,1)==False:
        if request.method=="POST":
            message=request.POST.get('message')
            support_id=int(request.POST.get('support_id'))
            if support_id==0:
                TechnicalSupportRequest.objects.create(user=request.user, message=message)
            else:
                try:
                    first_support=TechnicalSupportRequest.objects.get(id=int(support_id))
                except:
                    return HttpResponse("ERROR: Can't Reply on it")
                if first_support.continued_support==True:
                    return HttpResponse("Support details not found")
                if first_support.user!=request.user:
                    return HttpResponse("You never initiated this support message")
                TechnicalSupportRequest.objects.create(user=request.user, continued_support=True, main_support_id=support_id, message=message)
            return redirect('technical_support')
        else:
            responses=get_my_support_responses(request)
            support=responses[0]
            threads=responses[1]
            if support.count()==0:
                support="0"
            return render(request,'dashboard1/technical_support.html',context={"support": support, "threads": threads})
    return error_detection(request,1)

def get_my_support_responses(request):
    threads=[]
    responses=TechnicalSupportRequest.objects.filter(user=request.user, continued_support=False).order_by('-date')
    for each in responses:
        thread_responses=TechnicalSupportRequest.objects.filter(continued_support=True, main_support_id=each.id).order_by('date')
        threads.append(thread_responses)
    return [responses, threads]


def technical_support_assist(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_technical_support==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            message=request.POST.get('message')
            support_id=int(request.POST.get('support_id'))
            try:
                first_support=TechnicalSupportRequest.objects.get(id=int(support_id))
            except:
                return HttpResponse("ERROR: Can't Reply on it")
            if first_support.continued_support==True:
                return HttpResponse("Support details not found")
            TechnicalSupportRequest.objects.create(user=request.user, continued_support=True, main_support_id=support_id, message=message)
            return redirect('respond_support',support_id)
        else:
            support=TechnicalSupportRequest.objects.filter(continued_support=False).order_by('-date')
            if support.count()==0:
                support="0"
            return render(request,'dashboard1/assist_technical_support.html',context={"support": support, "permissions": permissions})
    return error_detection(request,1)

def respond_support(request,item):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_technical_support==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        try:
            support=TechnicalSupportRequest.objects.get(id=int(item))
        except:
            return HttpResponse("Support Details Not Found")
        if support.continued_support==True:
            return HttpResponse("Support Details Not Found")
        threads=get_all_threads(int(item))
        return render(request,'dashboard1/show_all_threads.html',context={"support": support, "threads": threads, "permissions": permissions})
    return error_detection(request,1)

def get_all_threads(id):
    threads=[]
    support=TechnicalSupportRequest.objects.get(id=id)
    thread_responses=TechnicalSupportRequest.objects.filter(continued_support=True, main_support_id=support.id).order_by('date')
    threads.append(thread_responses)
    return threads

def delete_account(request):
    if error_detection(request,1)==False:
        try:
            u=User.objects.get(username=request.user)
            email=u.email
            u.delete()
        except:
            return error_message(request,"User Not Found")
        subject = 'Account Deletion Notice'
        message = f'Hey, user!\nYour account has been sucessfully deleted from Clean Frame.\nMoreover all the records related are also deleted.\nIf you create a new account then previous effects or changes would not be shown.\nThanks'
        SENDMAIL(subject,message,email)
        return redirect('home')
    return error_detection(request,1)