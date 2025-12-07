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

""" Start of Creating Views for Authentication Section """

@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    """ Registration View """
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']

    otp = str(random.randint(1000, 9999))
    subject = "OTP for Registration"
    message = f"Your OTP code is {otp}. It is valid for 5 minutes."

    try:
        send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

        from django.core.cache import cache
        cache.set(f"reg_otp_{email}", {
            "otp": otp,
            "data": serializer.validated_data
        }, timeout=300) 

        return Response({
            "success": True,
            "message": f"OTP sent to {email}",
            "otp": otp
        })

    except Exception as e:
        print("Email error:", e)
        return Response({"success": False, "message": "Failed to send OTP"}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_registration_otp(request):
    """ Verify Registration OTP View """
    email = request.data.get("email")
    otp = request.data.get("otp")

    from django.core.cache import cache
    temp_data = cache.get(f"reg_otp_{email}")

    if not temp_data:
        return Response({"success": False, "message": "OTP expired or invalid"}, status=400)

    if temp_data['otp'] != otp:
        return Response({"success": False, "message": "Incorrect OTP"}, status=400)

    user_data = temp_data['data']
    password = user_data.pop("password")

    user = Users.objects.create(**user_data)
    user.set_password(password)
    user.save()

    cache.delete(f"reg_otp_{email}")

    return Response({
        "success": True,
        "message": "Registration completed",
        "user": GetProfileDataSerializer(user).data,
        "token": get_tokens_for_user(user)
    }, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def social_signup_signin(request):
    """ Social Signup Signin View """
    serializer = SocialSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user, created = serializer.create_or_get_user()
    user_data_serializer = GetProfileDataSerializer(instance=user)

    return Response({
        "success": True,
        'message': 'Successfully authenticated.',
        'user': user_data_serializer.data,
        'token': get_tokens_for_user(user),
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """ Login View """
    serializer = LoginSerialzer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data['user']

    user_data_serializer = GetProfileDataSerializer(instance=user)

    return Response({
        "success": True,
        'message': 'Successfully logged in.',
        'user': user_data_serializer.data,
        'token': get_tokens_for_user(user),
    }, status=status.HTTP_200_OK)
   
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """ Forgot Password View """
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
            "success": True,
            'message': f'OTP successfully sent to {email} || otp : {otp}'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print('error : ', e)
        return Response({
            "success": False,
            "message": "Failed to send OTP email."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def vaify_otp(request):
    """ Verify OTP View """
    serializer = VarifiedOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response({
        "success": True,
        'message': 'otp vairified'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_new_password(request):
    """ Reset New Password View """
    serializer = ResetNewPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response({
        "success": True,
        'message': 'Password updated successfully'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """ Change Password View """
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    serializer.save()

    return Response({
        "success": True,
        'message': 'Change password successfully'
    }, status=status.HTTP_200_OK)

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_data(request):
    """ Profile Data View """
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
            "success": True,
            'message': 'Profile updated successfully',
            'user': profile_serialzier.data
        }, status=status.HTTP_200_OK)

""" End of Creating Views for Authentication Section """
