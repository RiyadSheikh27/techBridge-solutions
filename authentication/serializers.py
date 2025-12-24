from rest_framework import serializers
from .models import Users
from django.utils import timezone
import os

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'password', 'image']

    def validate_email(self, value):
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            raise serializers.ValidationError({'error': 'Invalid email or password'})

        if not user.check_password(password):
            raise serializers.ValidationError({'error': 'Invalid email or password'})

        if not user.is_active:
            raise serializers.ValidationError({'error': 'Account is not active'})

        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            Users.objects.get(email=value)
        except Users.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(required=True, min_length=6, write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, min_length=6, write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name', 'email', 'image', 'role', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'created_at']


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'image']

    def update(self, instance, validated_data):
        """Update fields"""
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)

        """Handle image update"""
        new_image = validated_data.get('image', None)
        if new_image and new_image != instance.image:
            """Delete old image"""
            if instance.image:
                try:
                    if os.path.isfile(instance.image.path):
                        os.remove(instance.image.path)
                except Exception:
                    pass
            instance.image = new_image

        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """For admin to view all users"""
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name', 'email', 'image', 'role', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_users', 'total_active_users', 'total_inactive_users']

# class UserStatisticsSerializer(serializers.ModelSerializer):
#     """For admin to view user statistics"""
#     class Meta:
#         model = Users
#     pass

class UserStatusChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['is_active']
