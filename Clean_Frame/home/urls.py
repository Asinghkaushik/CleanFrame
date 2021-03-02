from django.urls import path
from .views import home, signup_student, signup_student_verify, signup_student_verify_otp,signup_student_resend_otp,signup_company,signup_company_verify,signup_company_verify_otp, signup_company_resend_otp,logout_request, login_request, forgot_password, forgot_password_verify_otp, forgot_password_resend_otp, reset_password,error

urlpatterns = [
    path('',home,name='home'),
    path('signup/student/',signup_student,name='signup_student'),
    path('signup/student/verify/',signup_student_verify, name='signup_student_verify'),
    path('signup/student/verify/otp/',signup_student_verify_otp, name='signup_student_verify_otp'),
    path('signup/student/verify/resendotp/<str:email>',signup_student_resend_otp, name='signup_student_resend_otp'),
    path('signup/company/',signup_company, name='signup_company'),
    path('signup/company/verify/',signup_company_verify,name='signup_company_verify'),
    path('signup/company/verify/otp/',signup_company_verify_otp,name='signup_company_verify_otp'),
    path('signup/company/verify/resendotp/<str:email>',signup_company_resend_otp,name='signup_company_resend_otp'),
    path('logout/',logout_request,name='logout_request'),
    path('login/',login_request, name='login_request'),
    path('password/forgot/',forgot_password, name="forgot_password"),
    path('password/forgot/verify/otp/',forgot_password_verify_otp, name="forgot_password_verify_otp"),
    path('password/forgot/resend/otp/<str:email>', forgot_password_resend_otp, name='forgot_password_resend_otp'),
    path('password/forgot/change/',reset_password, name='reset_password'),
    path('error/<str:message>',error,name="error"),

]