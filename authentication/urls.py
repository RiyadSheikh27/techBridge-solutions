from django.urls import path
from . import views

urlpatterns = [
    path('registration/', views.registration, name='registration'),
    path('verify_otp/', views.verify_registration_otp, name='verify_otp'),
    
    path('login/', views.login, name='login'),
    
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_new_password/', views.reset_password, name='reset_password'),
    path('change_password/', views.change_password, name='change_password'),
    
    path('profile_data/', views.get_profile, name='get_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    path('users/', views.user_list, name='user_list'),
]