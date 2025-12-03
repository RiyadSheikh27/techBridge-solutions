from rest_framework.serializers import ModelSerializer
from .models import Users 
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.utils import timezone
import os

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'image', 'auth_provider']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Users.objects.create(**validated_data)
        user.set_password(password)  
        user.save()
        return user
    
class SocialSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    auth_provider = serializers.CharField(required=True)    

    def create_or_get_user(self):
        data = self.validated_data
        user, created = Users.objects.get_or_create(
            email=data['email'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'auth_provider': data['auth_provider']
            }
        )
        return user, created

class LoginSerialzer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = get_object_or_404(Users, email=email)

        if not user.check_password(password):
            raise serializers.ValidationError({'error': '"email" or "password" wrong'})

        attrs['user'] = user
        return attrs
 
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        user = get_object_or_404(Users, email=email)
        
        attrs['user'] = user
        return super().validate(attrs)


class VarifiedOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        user = get_object_or_404(Users, email=email)

        if user.otp != otp:
            raise serializers.ValidationError({'otp': 'Invalid OTP.'})
        
        if user.otp_expired < timezone.now():
            raise serializers.ValidationError({'otp': 'OTP has expired.'})
        
        user.otp = None
        user.otp_expired = None
        user.save(update_fields=['otp', 'otp_expired'])

        return super().validate(attrs)
    
class ResetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def save(self, **kwargs):
        email = self.validated_data['email']
        password = self.validated_data['password']

        user = get_object_or_404(Users, email=email)

        user.set_password(password)
        user.save()

        return user 

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        password = attrs.get('current_password')

        if not user.check_password(password):
            raise serializers.ValidationError({'current_password': 'wrong current password'})
        
        return super().validate(attrs)

    def save(self, **kwargs):
        user = self.context['request'].user
        password = self.validated_data['new_password']
        user.set_password(password)
        user.save()
        return user

class GetProfileDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name', 'email', 'image', 'auth_provider']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'image', 'email']

    def update(self, instance, validated_data):
        new_image = validated_data.get('image', None)
        if new_image and new_image != instance.image:
            if instance.image and os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
            instance.image = new_image

        return super().update(instance, validated_data)
    
    def update(self, instance, validated_data):
        if 'first_name' in validated_data and validated_data['first_name']:
            instance.first_name = validated_data['first_name']
        if 'last_name' in validated_data and validated_data['last_name']:
            instance.last_name = validated_data['last_name']

        if 'email' in validated_data and validated_data['email']:
            new_email = validated_data['email']
            if new_email != instance.email:
                if Users.objects.filter(email=new_email).exclude(id=instance.id).exists():
                    raise serializers.ValidationError({"email": "This email is already in use."})
                instance.email = new_email

        new_image = validated_data.get('image', None)
        if new_image and new_image != instance.image:
            if instance.image and os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
            instance.image = new_image

        instance.save()
        return instance

