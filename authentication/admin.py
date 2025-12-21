from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Users


@admin.register(Users)
class UsersAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'image_preview', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('email', 'first_name', 'last_name', 'image')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('OTP Information', {
            'fields': ('otp', 'otp_expired'),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('created_at', 'updated_at', 'last_login')
        }),
    )
    
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'