from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Custom save to work with your Users model
        """
        user = super().save_user(request, user, form, commit=False)
        user.is_active = True  # Auto-activate social users
        if commit:
            user.save()
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Handle the case where social account email already exists
        """
        if sociallogin.is_existing:
            return

        try:
            from .models import Users
            email = sociallogin.account.extra_data.get('email', '').lower()
            
            if email:
                user = Users.objects.get(email=email)
                sociallogin.connect(request, user)
        except Users.DoesNotExist:
            pass

    def populate_user(self, request, sociallogin, data):
        """
        Populate user instance with data from social provider
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Set additional fields
        if not user.first_name:
            user.first_name = data.get('first_name', '')
        if not user.last_name:
            user.last_name = data.get('last_name', '')
        
        # Auto-activate social login users
        user.is_active = True
        
        return user