from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
# Create your models here.

class Users(AbstractUser):
    username = models.CharField(blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='users/', blank=True, null=True)
    otp = models.CharField(max_length=4, blank=True, null=True)
    otp_expired = models.DateTimeField(blank=True, null=True)
    auth_provider = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if self.otp:
            self.otp_expired = timezone.now() + timedelta(minutes=5)
        return super().save(*args, **kwargs)

