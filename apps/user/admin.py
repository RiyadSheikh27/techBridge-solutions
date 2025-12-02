from django.contrib import admin
from apps.user.models import Users
from django.contrib.auth.admin import UserAdmin
# Register your models here.

@admin.register(Users)
class UserAdmin(UserAdmin):
    list_display = [field.name for field in Users._meta.fields if field.name != 'password']
