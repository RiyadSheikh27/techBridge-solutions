from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView,
)

urlpatterns = [
    path('registration/', registration, name='registration'),
    path('social_signup_signin/', social_signup_signin, name='social_signup_signin'),

    path('login/', login, name='login'),
    path('forgot_password/', forgot_password, name='forgot_password'),

    path('vaify_otp/', vaify_otp, name='vaify_otp'),
    path('reset_new_password/', reset_new_password, name='reset_new_password'),
    path('change_password/', change_password, name='change_password'),
    
    path('profile_data/', profile_data, name='profile_data'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
]

