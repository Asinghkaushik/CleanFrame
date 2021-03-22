from django.urls import path
from .views import dashboard,profile,send_otp_to_phone_stu,verify_otp_phone_stu,resend_otp_to_phone_stu,send_otp_to_phone_com,verify_otp_phone_com,resend_otp_to_phone_com, staff_profile,student_profile_3,company_profile_2, student_profile_2,student_profile_1,student_company_number,change_password,student_account_signup_permit,student_account_signup_action,company_account_signup_permit,company_account_signup_action
from .views import new_announcement_round, new_announcement,new_announcement_success, announcements, edit_announcement,stu_result, show_companies, show_company_round_details, register_student_first_round_only, show_registrations, announce_internship, internships, edit_internship
from .views import delete_internship, delete_announcement, check_student_profile, seeze_results, internship_result, restrict_users, ban_user_account_permanent, delete_staff_account_admin

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
    path('announcement/new/round/',new_announcement_round,name="new_announcement_round"),
    path('announcement/new/',new_announcement,name="new_announcement"),
    path('announcement/new/success/<str:item>',new_announcement_success,name="new_announcement_success"),
    path('announcements/',announcements,name="announcements"),
    path('announcements/edit/<str:item>/',edit_announcement,name="edit_announcement"),
    path('announcements/result/<str:item>', stu_result, name="stu_result"),
    path('register/company/',show_companies,name="show_companies"),
    path('show/company/details/<str:item>',show_company_round_details,name="show_company_round_details"),
    path('register/company/round/1/id/<str:item>',register_student_first_round_only,name="register_student_first_round_only"),
    path('show/student/registrations/all/',show_registrations,name="show_registrations"),
    path('announcements/internship/',announce_internship,name="announce_internship"),    
    path('show/internships/all/',internships,name="internships"),
    path('internships/edit/<str:item>',edit_internship,name="edit_internship"),
    path('internships/delete/<str:item>',delete_internship,name="delete_internship"),
    path('announcement/delete/<str:item>',delete_announcement,name="delete_announcement"),
    path('profile/student/<str:item>',check_student_profile,name="check_student_profile"),
    path('results/seeze/<str:item>',seeze_results,name="seeze_results"),
    path('internships/result/<str:item>',internship_result,name="internship_result"),
    path('staff/restrict/users/',restrict_users,name="restrict_users"),
    path('staff/restrict/user/<str:item>',ban_user_account_permanent,name="ban_user_account_permanent"),
    path('staff/restrict/staff/delete/account/<str:item>',delete_staff_account_admin,name="delete_staff_account_admin"),
        
        

]