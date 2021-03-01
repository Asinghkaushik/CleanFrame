from django.urls import path
from .views import dashboard,profile,send_otp_to_phone_stu,verify_otp_phone_stu,resend_otp_to_phone_stu,send_otp_to_phone_com,verify_otp_phone_com,resend_otp_to_phone_com, staff_profile,student_profile_3,company_profile_2, student_profile_2,student_profile_1,student_company_number,change_password

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

]