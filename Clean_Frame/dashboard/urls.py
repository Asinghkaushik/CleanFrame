from django.urls import path
from .views import dashboard,profile,send_otp_to_phone_stu,verify_otp_phone_stu,resend_otp_to_phone_stu,send_otp_to_phone_com,verify_otp_phone_com,resend_otp_to_phone_com

urlpatterns = [
    path('',dashboard,name="dashboard"),
    path('profile/',profile,name="profile"),
    path('send/otp/phone/student/',send_otp_to_phone_stu,name="send_otp_to_phone_stu"),
    path('send/otp/phone/student/verify/',verify_otp_phone_stu,name="verify_otp_phone_stu"),
    path('resend/otp/phone/student/',resend_otp_to_phone_stu,name="resend_otp_to_phone_stu"),
    path('send/otp/phone/company/',send_otp_to_phone_com,name="send_otp_to_phone_com"),
    path('send/otp/phone/compnay/verify/',verify_otp_phone_com,name="verify_otp_phone_com"),
    path('resend/otp/phone/company/',resend_otp_to_phone_com,name="resend_otp_to_phone_com"),


]