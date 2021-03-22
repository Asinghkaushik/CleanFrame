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
from .models import StaffPermissions, CompanyAnnouncement, InternshipFinalResult, StudentRegistration, Internship, ProfilePermissions
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
        SENDMAIL(subject,message,email)

def notify_other_students_for_rejection(request, prev, new):
    get_students=StudentRegistration.objects.filter(company=prev, result_status=0)
    for each in get_students:
        each.result_status=2
        each.save()
        subject = 'Internship Round Result'
        message = f'Hi user, We feel apology telling you that you have been rejected in an internship round.\nDetails of this round are as follows:\nCompany Name: '+str(each.company.company.first_name)+'\nInternship Name: '+str(each.company.internship.internship_name)+'\nRound Number: '+str(each.company.internship_round)+'\nThanks'
        email=each.student.email
        SENDMAIL(subject,message,email)

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
                        SENDMAIL(subject,message,email)
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
                        SENDMAIL(subject,message,email)
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
            SENDMAIL(subject,message,email)
        if each.result_status==0:
            each.result_status=2
            each.save()
            subject = 'Internship Result Last Round'
            message = f'Hi user, you have been rejected in the last round of internship, you can try for another interships.\nDetails of this round are as follows:\nCompany Name: '+str(each.company.company.first_name)+'\nInternship Name: '+str(each.company.internship.internship_name)+'\nRound Number: '+str(each.company.internship_round)+' (last Round)\nThanks'
            email=each.student.email
            SENDMAIL(subject,message,email)
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
            SENDMAIL(subject,message,email)
            
            
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
        if check_profilepage_permissions(request, item) == False:
            return HttpResponse("You have not permission to view this user's profile page")
        image=data.image
        return render(request,'dashboard/profile_page.html',context={"data": data, "image": image})
    return error_detection(request,1)

def check_profilepage_permissions(request, item):
    try:
        user_profile=User.objects.get(id=int(item))
    except:
        return HttpResponse("Profile Not Found")
    try:
        if request.user == user_profile:
            return True
    except:
        try:
            ProfilePermissions.objects.get(user_who_can_see=request.user,user_whose_to_see=user_profile)
            return True
        except:
            #Check the permissions give by user
            return False

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
            if permissions.can_ban_users==False:
                return HttpResponse("404 Error: You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        normal_users=get_simple_users(request)
        staff_users={}
        if request.user.is_superuser:
            staff_users=User.objects.filter(is_active=True, is_staff=True)
        return render(request,'dashboard1/ban_users.html',context={"normal_users": normal_users, "staff_users": staff_users, "permissions": permissions})
    return error_detection(request,1)

def get_simple_users(request):
    if request.user.is_staff==False:
        return HttpResponse("404: ERROR")
    users=User.objects.filter(is_staff=False, is_active=True, is_superuser=False)
    for each in users:
        profile=get_the_profile(each)
        if profile=={}:
            users.exclude(id=each.id)
        elif profile.account_banned_permanent or profile.account_banned_temporary:
            users.exclude(id=each.id)
    return users