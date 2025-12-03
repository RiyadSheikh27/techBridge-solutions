from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from .serializers import *
from .models import *
from .utils import *
from rest_framework.permissions import IsAuthenticated, AllowAny
import random
from django.core.mail import send_mail

# Create your views here.
@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save() 

    token = get_tokens_for_user(user)

    return Response({
        'message': 'User registered successfully',
        'user': RegistrationSerializer(user).data, 
        'token': token,
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def social_signup_signin(request):
    serializer = SocialSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user, created = serializer.create_or_get_user()
    user_data_serializer = GetProfileDataSerializer(instance=user)

    return Response({
        'message': 'Successfully authenticated.',
        'user': user_data_serializer.data,
        'token': get_tokens_for_user(user),
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerialzer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data['user']

    user_data_serializer = GetProfileDataSerializer(instance=user)

    return Response({
        'message': 'Successfully logged in.',
        'user': user_data_serializer.data,
        'token': get_tokens_for_user(user),
    }, status=status.HTTP_200_OK)
   
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email =  serializer.validated_data['email']
    user = serializer.validated_data['user']

    otp = str(random.randint(1000, 9999))
    subject = 'Forgot Password OTP'
    message = f'Your OTP code is {otp}. It is valid for 5 minutes.'

    try:
        send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        user.otp = otp
        user.save(update_fields=['otp', 'otp_expired']) 

        return Response({
            'status': 'succes',
            'message': f'OTP successfully sent to {email} || otp : {otp}'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print('error : ', e)
        return Response({
            'status': 'error',
            "message": "Failed to send OTP email."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def vaify_otp(request):
    serializer = VarifiedOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response({
        'status': 'success',
        'message': 'otp vairified'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_new_password(request):
    serializer = ResetNewPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response({
        'status': 'success',
        'message': 'Password updated successfully'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    serializer.save()

    return Response({
        'status': 'success',
        'message': 'Change password successfully'
    }, status=status.HTTP_200_OK)

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_data(request):
    user = request.user
    if request.method == 'GET':
        serialzier = GetProfileDataSerializer(instance=user)
    
        return Response({
            'message': 'get user successfully',
            'user': serialzier.data, 
        }, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        serializer = ProfileUpdateSerializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        profile_serialzier = GetProfileDataSerializer(instance=user)
    
        return Response({
            'message': 'Profile updated successfully',
            'user': profile_serialzier.data
        }, status=status.HTTP_200_OK)

