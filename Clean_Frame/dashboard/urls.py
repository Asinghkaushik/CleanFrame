from django.urls import path
from .views import dashboard,profile,send_otp_to_phone_stu,verify_otp_phone_stu,resend_otp_to_phone_stu,send_otp_to_phone_com,verify_otp_phone_com,resend_otp_to_phone_com, staff_profile,student_profile_3,company_profile_2, student_profile_2,student_profile_1,student_company_number,change_password,student_account_signup_permit,student_account_signup_action,company_account_signup_permit,company_account_signup_action
from .views import new_announcement,new_announcement_success

urlpatterns = [
    path('',dashboard,name="dashboard"),
    path('profile/',profile,name="profile"),
    path('send/otp/phone/student/',send_otp_to_phone_stu,name="send_otp_to_phone_stu"),
    path('send/otp/phone/student/verify/',verify_otp_phone_stu,name="verify_otp_phone_stu"),
    path('resend/otp/phone/student/',resend_otp_to_phone_stu,name="resend_otp_to_phone_stu"),
    path('send/otp/phone/company/',send_otp_to_phone_com,name="send_otp_to_phone_com"),
    path('send/otp/phone/compnay/verify/',verify_otp_phone_com,name="verify_otp_phone_com"),
    path('resend/otp/phone/company/',resend_otp_to_phone_com,name="resend_otp_to_phone_com"),
    path('profile/upload/staff/',staff_profile,name="staff_profile"),
    path('profile/upload/student/3/',student_profile_3,name="student_profile_3"),
    path('profile/upload/company/2/',company_profile_2,name="company_profile_2"),
    path('profile/upload/student/2/',student_profile_2,name="student_profile_2"),
    path('profile/upload/student/1/',student_profile_1,name="student_profile_1"),
    path('profile/upload/phone_number/',student_company_number,name="student_company_number"),
    path('profile/changepassword/',change_password,name="change_password"),
    path('permit/signup_request/student/',student_account_signup_permit,name="student_account_signup_permit"),
    path('permit/signup_request/student/<str:type>/<str:item>',student_account_signup_action,name="student_account_signup_action"),
    path('permit/signup_request/company/',company_account_signup_permit,name="company_account_signup_permit"),
    path('permit/signup_request/company/<str:type>/<str:item>',company_account_signup_action,name="company_account_signup_action"),
    path('announcement/new/',new_announcement,name="new_announcement"),
    path('announcement/new/success/',new_announcement_success,name="new_announcement_success"),
    
    

]