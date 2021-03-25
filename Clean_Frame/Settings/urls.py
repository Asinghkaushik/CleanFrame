from django.urls import path
from .views import settings_home


urlpatterns = [
    path('',settings_home,name="settings_home"), 
    # path('account/delete/',delete_account,name="delete_account"),


]