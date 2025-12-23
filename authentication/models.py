import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from datetime import timedelta
 
class CustomUserManager(UserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=True, is_superuser=True, **extra_fields)
        user.set_password(password)
        user.role = 'admin'
        user.is_active = True
        user.username = email.split('@')[0]
        user.save(using=self._db)
        return user
 
 

class Users(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='users/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expired = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if self.otp:
            self.otp_expired = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)