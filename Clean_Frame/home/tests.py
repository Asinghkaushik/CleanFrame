from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import (login,authenticate,logout)
from home.models import StudentProfile

# Create your tests here.
#Notes: 
#   1.There must be method in every class named as setUp(self) which will set variables and databases for unit testcase
#   2. A tearDown(self) can be used to clear all the databases created after the test cases run
#   3. Every testcase method must start from 'test' otherwise it will be treated like a function not testcase.

#Checks for all the functions and methods used for login form
class LoginTest(TestCase):

    #Create a new user to test for login phase
    #Create a new student profile with the user create in Setup() method
    #There are more fields in the profile which would be set to default if not given in the create() function
    def setUp(self):
        self.user = User.objects.create_user(username="ABCDE", password="ABCDE@123", email="ABCDE@gmail.com")
        self.user.save()
        self.user.is_staff=True
        self.user.save()
        self.new_profile=StudentProfile.objects.create(user=self.user, gender="Male", verified=True, account_banned_permanent=False, account_banned_temporary=False, account_ban_time=0)
        self.new_profile.save()

    #To delete user account after test cases
    def tearDown(self):
        self.user.delete()
        self.new_profile.delete()

    #Checks for when correct username and password is given
    def test_correct_username_password(self):
        user=authenticate(username="ABCDE", password="ABCDE@123")
        self.assertTrue((user is not None) and user.is_authenticated)

    #Checks for when correct email and password is given
    def test_correct_email_password(self):
        getuser=User.objects.get(email="ABCDE@gmail.com").username
        user=authenticate(username=getuser, password="ABCDE@123")
        self.assertTrue((user is not None) and user.is_authenticated)

    #Checks when wrong username is given
    def test_wrong_username(self):
        user=authenticate(username="ABCE", password="ABCDE@123")
        self.assertFalse(user is not None and user.is_authenticated)

    #Checks when wrong password is given
    def test_wrong_password(self):
        user=authenticate(username="ABCDE", password="ABCDE@113")
        self.assertFalse(user is not None and user.is_authenticated)

    #Checks whether student account is banned or not
    def test_account_ban(self):
        isbanned=self.new_profile.account_banned_permanent or self.new_profile.account_banned_temporary
        
        #If user is banned then assertTrue will return '.' , else assertFalse will return '.' 
        if isbanned:
            self.assertTrue(isbanned)
        else:
            self.assertFalse(isbanned)

    #Checks for staff user
    def test_staff(self):
        is_staff=self.user.is_staff
        if is_staff:
            self.assertTrue(is_staff)
        else:
            self.assertFalse(is_staff)
            
    #Checks for admin user
    def test_admin(self):
        is_admin=self.user.is_superuser
        if is_admin:
            self.assertTrue(is_admin)
        else:
            self.assertFalse(is_admin)