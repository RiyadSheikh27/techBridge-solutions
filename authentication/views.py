from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from .models import Users
from .serializers import *
from .utils import get_tokens_for_user
from .permissions import IsAdmin
import random
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    """Step 1: Register user and send OTP"""
    serializer = RegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    otp = str(random.randint(1000, 9999))
    
    try:
        subject = 'Email Verification - OTP'

        text_message = f"""
Email Verification

Your OTP for registration is: {otp}

This OTP is valid for 5 minutes.
Do not share this code with anyone.
"""

        html_message = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Email Verification</title>
</head>
<body style="margin:0;padding:0;background-color:#0a0a0a;font-family:'Georgia',serif;">

  <table width="100%" cellpadding="0" cellspacing="0" border="0"
         style="background-color:#0a0a0a;padding:48px 16px;">
    <tr>
      <td align="center">

        <!-- Card -->
        <table width="560" cellpadding="0" cellspacing="0" border="0"
               style="max-width:560px;width:100%;background-color:#141414;
                      border-radius:2px;overflow:hidden;border:1px solid #242424;">

          <!-- Top accent bar -->
          <tr>
            <td style="background:linear-gradient(90deg,#c8a96e 0%,#f0d090 50%,#c8a96e 100%);
                       height:4px;font-size:0;line-height:0;">&nbsp;</td>
          </tr>

          <!-- Header -->
          <tr>
            <td style="padding:44px 48px 36px;text-align:center;
                       border-bottom:1px solid #242424;">

              <!-- Shield / Lock Icon -->
              <div style="display:inline-block;margin-bottom:24px;">
                <table cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="background:linear-gradient(135deg,#1e1e1e,#2a2a2a);
                               border:1px solid #333;border-radius:50%;
                               width:72px;height:72px;text-align:center;
                               vertical-align:middle;">
                      <div style="font-size:30px;line-height:72px;">🔐</div>
                    </td>
                  </tr>
                </table>
              </div>

              <p style="margin:0 0 8px;font-size:11px;letter-spacing:5px;
                         color:#c8a96e;text-transform:uppercase;
                         font-family:'Courier New',monospace;">Security Verification</p>
              <h1 style="margin:0;font-size:26px;font-weight:normal;
                         color:#f5f0e8;font-family:'Georgia',serif;
                         letter-spacing:-0.3px;line-height:1.2;">
                Verify Your Email
              </h1>
              <p style="margin:12px 0 0;font-size:13px;color:#666;
                         font-family:'Courier New',monospace;letter-spacing:0.5px;line-height:1.6;">
                Enter the code below to complete<br/>your registration.
              </p>
            </td>
          </tr>

          <!-- OTP Block -->
          <tr>
            <td style="padding:44px 48px 36px;text-align:center;">

              <p style="margin:0 0 20px;font-size:10px;letter-spacing:4px;
                         color:#888;text-transform:uppercase;
                         font-family:'Courier New',monospace;">Your One-Time Password</p>

              <!-- OTP Digits -->
              <table cellpadding="0" cellspacing="0" border="0"
                     style="margin:0 auto 32px;">
                <tr>
                  {"".join([f'''
                  <td style="padding:0 6px;">
                    <div style="width:58px;height:72px;
                                background:linear-gradient(180deg,#1e1e1e 0%,#191919 100%);
                                border:1px solid #333;border-bottom:3px solid #c8a96e;
                                border-radius:2px;text-align:center;line-height:72px;
                                font-size:32px;font-weight:bold;color:#f5f0e8;
                                font-family:'Courier New',monospace;letter-spacing:0;">
                      {digit}
                    </div>
                  </td>
                  ''' for digit in otp])}
                </tr>
              </table>

              <!-- Timer note -->
              <table cellpadding="0" cellspacing="0" border="0"
                     style="margin:0 auto 36px;background:#1a1a1a;
                            border:1px solid #2a2a2a;border-radius:2px;">
                <tr>
                  <td style="padding:12px 24px;">
                    <p style="margin:0;font-size:11px;color:#c8a96e;
                               font-family:'Courier New',monospace;
                               letter-spacing:2px;text-transform:uppercase;">
                      ⏱ &nbsp;Valid for 5 minutes only
                    </p>
                  </td>
                </tr>
              </table>

              <!-- Divider -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="margin-bottom:28px;">
                <tr>
                  <td style="border-top:1px solid #222;height:1px;font-size:0;">&nbsp;</td>
                </tr>
              </table>

              <!-- Warning -->
              <table cellpadding="0" cellspacing="0" border="0"
                     style="margin:0 auto;background:#1c1510;
                            border:1px solid #3a2a10;border-left:3px solid #c8a96e;
                            border-radius:0 2px 2px 0;max-width:400px;">
                <tr>
                  <td style="padding:14px 18px;text-align:left;">
                    <p style="margin:0;font-size:11px;color:#a08050;
                               font-family:'Courier New',monospace;
                               letter-spacing:0.5px;line-height:1.7;">
                      <strong style="color:#c8a96e;">⚠ Do not share</strong> this code with anyone.<br/>
                      We will never ask for your OTP via phone or email.
                    </p>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- Didn't request note -->
          <tr>
            <td style="padding:20px 48px 32px;text-align:center;
                       border-top:1px solid #1e1e1e;">
              <p style="margin:0;font-size:11px;color:#444;
                         font-family:'Courier New',monospace;letter-spacing:0.5px;line-height:1.7;">
                Didn't create an account?<br/>
                <span style="color:#666;">You can safely ignore this email.</span>
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 48px;border-top:1px solid #1e1e1e;
                       background-color:#0f0f0f;">
              <p style="margin:0;font-size:10px;color:#333;
                         font-family:'Courier New',monospace;
                         letter-spacing:1px;text-align:center;">
                &copy; 2026 Techbridge Solution &nbsp;&mdash;&nbsp; Automated Security Email
              </p>
            </td>
          </tr>

          <!-- Bottom accent bar -->
          <tr>
            <td style="background:linear-gradient(90deg,#c8a96e 0%,#f0d090 50%,#c8a96e 100%);
                       height:2px;font-size:0;line-height:0;">&nbsp;</td>
          </tr>

        </table>
        <!-- /Card -->

      </td>
    </tr>
  </table>

</body>
</html>"""

        from django.core.mail import EmailMultiAlternatives
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send(fail_silently=False)

        cache.set(f'registration_{email}', {
            'otp': otp,
            'data': serializer.validated_data
        }, timeout=300)
        print(otp)
        
        return Response({
            'success': True,
            'message': f'OTP sent to {email}',
            'email': email
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to send OTP. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def verify_registration_otp(request):
#     """Step 2: Verify OTP for both registration and password reset"""
#     serializer = VerifyOTPSerializer(data=request.data)
    
#     if not serializer.is_valid():
#         return Response({
#             'success': False,
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

#     email = serializer.validated_data['email']
#     otp = serializer.validated_data['otp']
    
#     """Check for registration OTP"""
#     registration_data = cache.get(f'registration_{email}')
#     if registration_data and registration_data['otp'] == otp:
#         try:
#             user_data = registration_data['data']
#             password = user_data.pop('password')
            
#             user = Users.objects.create(**user_data)
#             user.set_password(password)
#             user.is_active = True
#             user.save()
            
#             cache.delete(f'registration_{email}')
#             tokens = get_tokens_for_user(user)
            
#             return Response({
#                 'success': True,
#                 'message': 'Registration completed successfully',
#                 'user': UserProfileSerializer(user).data,
#                 'tokens': tokens
#             }, status=status.HTTP_201_CREATED)
            
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': 'Failed to create user. Please try again.'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     password_reset_otp = cache.get(f'password_reset_{email}')
#     if password_reset_otp and password_reset_otp == otp:
#         cache.set(f'verified_{email}', True, timeout=60)
        
#         return Response({
#             'success': True,
#             'message': 'OTP verified successfully. Please set your new password.',
#             'email': email
#         }, status=status.HTTP_200_OK)
    
#     """If no match found"""
#     return Response({
#         'success': False,
#         'message': 'Invalid or expired OTP.'
#     }, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_registration_otp(request):
    """Step 2: Verify OTP for both registration and password reset"""
    serializer = VerifyOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    otp = serializer.validated_data['otp']
    
    # Check for registration OTP
    registration_data = cache.get(f'registration_{email}')
    if registration_data and registration_data['otp'] == otp:
        try:
            user_data = registration_data['data'].copy()  # Fix: copy to avoid mutating cached object
            password = user_data.pop('password')
            
            user = Users.objects.create(**user_data)
            user.set_password(password)
            user.is_active = True
            user.save()
            
            cache.delete(f'registration_{email}')
            tokens = get_tokens_for_user(user)
            
            return Response({
                'success': True,
                'message': 'Registration completed successfully',
                'user': UserProfileSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Registration error for {email}: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to create user. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Check for password reset OTP
    password_reset_otp = cache.get(f'password_reset_{email}')
    if password_reset_otp and password_reset_otp == otp:
        cache.set(f'verified_{email}', True, timeout=60)
        
        return Response({
            'success': True,
            'message': 'OTP verified successfully. Please set your new password.',
            'email': email
        }, status=status.HTTP_200_OK)
    
    # If no match found
    return Response({
        'success': False,
        'message': 'Invalid or expired OTP.'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user"""
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.validated_data['user']
    tokens = get_tokens_for_user(user)
    
    return Response({
        'success': True,
        'message': 'Login successful',
        'user': UserProfileSerializer(user).data,
        'tokens': tokens
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Send OTP for password reset"""
    serializer = ForgotPasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    otp = str(random.randint(1000, 9999))
    
    try:
        subject = 'Password Reset - OTP'

        text_message = f"""
Password Reset Request

Your OTP for password reset is: {otp}

This OTP is valid for 5 minutes.
If you did not request a password reset, please ignore this email.
Do not share this code with anyone.
"""

        html_message = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Password Reset</title>
</head>
<body style="margin:0;padding:0;background-color:#0a0a0a;font-family:'Georgia',serif;">

  <table width="100%" cellpadding="0" cellspacing="0" border="0"
         style="background-color:#0a0a0a;padding:48px 16px;">
    <tr>
      <td align="center">

        <!-- Card -->
        <table width="560" cellpadding="0" cellspacing="0" border="0"
               style="max-width:560px;width:100%;background-color:#141414;
                      border-radius:2px;overflow:hidden;border:1px solid #242424;">

          <!-- Top accent bar — red tone for password reset -->
          <tr>
            <td style="background:linear-gradient(90deg,#8b2020 0%,#c0392b 40%,#e74c3c 60%,#c0392b 80%,#8b2020 100%);
                       height:4px;font-size:0;line-height:0;">&nbsp;</td>
          </tr>

          <!-- Header -->
          <tr>
            <td style="padding:44px 48px 36px;text-align:center;
                       border-bottom:1px solid #242424;">

              <!-- Icon -->
              <div style="display:inline-block;margin-bottom:24px;">
                <table cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="background:linear-gradient(135deg,#1e1212,#2a1a1a);
                               border:1px solid #3a2020;border-radius:50%;
                               width:72px;height:72px;text-align:center;
                               vertical-align:middle;">
                      <div style="font-size:30px;line-height:72px;">🔑</div>
                    </td>
                  </tr>
                </table>
              </div>

              <p style="margin:0 0 8px;font-size:11px;letter-spacing:5px;
                         color:#e74c3c;text-transform:uppercase;
                         font-family:'Courier New',monospace;">Password Reset</p>
              <h1 style="margin:0;font-size:26px;font-weight:normal;
                         color:#f5f0e8;font-family:'Georgia',serif;
                         letter-spacing:-0.3px;line-height:1.2;">
                Reset Your Password
              </h1>
              <p style="margin:12px 0 0;font-size:13px;color:#666;
                         font-family:'Courier New',monospace;letter-spacing:0.5px;line-height:1.6;">
                We received a request to reset your password.<br/>
                Use the code below to proceed.
              </p>
            </td>
          </tr>

          <!-- OTP Block -->
          <tr>
            <td style="padding:44px 48px 36px;text-align:center;">

              <p style="margin:0 0 20px;font-size:10px;letter-spacing:4px;
                         color:#888;text-transform:uppercase;
                         font-family:'Courier New',monospace;">Your Reset Code</p>

              <!-- OTP Digits -->
              <table cellpadding="0" cellspacing="0" border="0"
                     style="margin:0 auto 32px;">
                <tr>
                  {"".join([f'''
                  <td style="padding:0 6px;">
                    <div style="width:58px;height:72px;
                                background:linear-gradient(180deg,#1e1212 0%,#191010 100%);
                                border:1px solid #3a2020;border-bottom:3px solid #e74c3c;
                                border-radius:2px;text-align:center;line-height:72px;
                                font-size:32px;font-weight:bold;color:#f5f0e8;
                                font-family:'Courier New',monospace;">
                      {digit}
                    </div>
                  </td>
                  ''' for digit in otp])}
                </tr>
              </table>

              <!-- Timer badge -->
              <table cellpadding="0" cellspacing="0" border="0"
                     style="margin:0 auto 36px;background:#1a1212;
                            border:1px solid #2e1a1a;border-radius:2px;">
                <tr>
                  <td style="padding:12px 24px;">
                    <p style="margin:0;font-size:11px;color:#e74c3c;
                               font-family:'Courier New',monospace;
                               letter-spacing:2px;text-transform:uppercase;">
                      ⏱ &nbsp;Expires in 5 minutes
                    </p>
                  </td>
                </tr>
              </table>

              <!-- Divider -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="margin-bottom:28px;">
                <tr>
                  <td style="border-top:1px solid #222;height:1px;font-size:0;">&nbsp;</td>
                </tr>
              </table>

              <!-- Warning strip -->
              <table cellpadding="0" cellspacing="0" border="0"
                     style="margin:0 auto;background:#1c1010;
                            border:1px solid #3a1a1a;border-left:3px solid #e74c3c;
                            border-radius:0 2px 2px 0;max-width:420px;">
                <tr>
                  <td style="padding:14px 18px;text-align:left;">
                    <p style="margin:0;font-size:11px;color:#a05050;
                               font-family:'Courier New',monospace;
                               letter-spacing:0.5px;line-height:1.7;">
                      <strong style="color:#e74c3c;">⚠ Security notice:</strong> Do not share this code.<br/>
                      We will never ask for your OTP via phone or chat.
                    </p>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- Didn't request note -->
          <tr>
            <td style="padding:20px 48px 32px;text-align:center;
                       border-top:1px solid #1e1e1e;">

              <!-- Alert box -->
              <table cellpadding="0" cellspacing="0" border="0"
                     style="margin:0 auto;background:#161616;
                            border:1px solid #2a2a2a;border-radius:2px;max-width:380px;">
                <tr>
                  <td style="padding:14px 20px;">
                    <p style="margin:0;font-size:11px;color:#555;
                               font-family:'Courier New',monospace;
                               letter-spacing:0.5px;line-height:1.8;">
                      Didn't request a password reset?<br/>
                      <span style="color:#444;">Your account is safe — ignore this email.<br/>
                      Consider changing your password if concerned.</span>
                    </p>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 48px;border-top:1px solid #1e1e1e;
                       background-color:#0f0f0f;">
              <p style="margin:0;font-size:10px;color:#333;
                         font-family:'Courier New',monospace;
                         letter-spacing:1px;text-align:center;">
                &copy; 2026 Techbridge Solution &nbsp;&mdash;&nbsp; Automated Security Email
              </p>
            </td>
          </tr>

          <!-- Bottom accent bar -->
          <tr>
            <td style="background:linear-gradient(90deg,#8b2020 0%,#c0392b 40%,#e74c3c 60%,#c0392b 80%,#8b2020 100%);
                       height:2px;font-size:0;line-height:0;">&nbsp;</td>
          </tr>

        </table>
        <!-- /Card -->

      </td>
    </tr>
  </table>

</body>
</html>"""

        from django.core.mail import EmailMultiAlternatives
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send(fail_silently=False)

        cache.set(f'password_reset_{email}', otp, timeout=300)

        return Response({
            'success': True,
            'message': f'OTP sent to {email}',
            'email': email
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to send OTP. Please try again. {e}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password after OTP verification"""
    serializer = ResetPasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    new_password = serializer.validated_data['new_password']
    
    """ Check if OTP was verified"""
    is_verified = cache.get(f'verified_{email}')
    if not is_verified:
        return Response({
            'success': False,
            'message': 'Please verify OTP first.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = Users.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        
        """ Clean up cache"""
        cache.delete(f'password_reset_{email}')
        cache.delete(f'verified_{email}')
        
        return Response({
            'success': True,
            'message': 'Password reset successfully'
        }, status=status.HTTP_200_OK)
        
    except Users.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password for authenticated user"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    new_password = serializer.validated_data['new_password']
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'success': True,
        'message': 'Password changed successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Get user profile"""
    serializer = UserProfileSerializer(request.user)
    return Response({
        'success': True,
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    serializer = UpdateProfileSerializer(
        request.user, 
        data=request.data, 
        partial=True
    )
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer.save()
    
    return Response({
        'success': True,
        'message': 'Profile updated successfully',
        'user': UserProfileSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdmin])
def user_list(request):
    """Get all users (Admin only)"""
    users = Users.objects.all().order_by('-created_at')

    total_users = users.count()
    total_active_users = users.filter(is_active=True).count()
    total_inactive_users = users.filter(is_active=False).count()

    serializer = UserListSerializer(users, many=True)
    
    return Response({
        'success': True,
        'messgae': "Users retrieved successfully",
        'statistics': {
            'total_users': total_users,
            'total_active_users': total_active_users,
            'total_inactive_users': total_inactive_users
        },
        'users': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAdmin])
def ChangeUserStatus(request, user_id):
    user = get_object_or_404(Users, id=user_id)
    serializer = UserStatusChangeSerializer(user, data=request.data)

    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer.save()
    return Response({
        'success': True,
        'message': 'User status changed successfully',
        'user': UserStatusChangeSerializer(user).data
    }, status=status.HTTP_200_OK)


