from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

class ContantInfoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Contact Information with custom responses
    """
    queryset = contantInfo.objects.all()
    serializer_class = contantInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Contact info list retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Contact info retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
    
        self._send_admin_notification(serializer.validated_data)
    
        return Response({
            "success": True,
            "message": "Request quote created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "message": "Contact info updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Contact info deleted successfully"
        }, status=status.HTTP_200_OK)

class RequestQuoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RequestQuote with custom JSON responses
    """
    queryset = RequestQuote.objects.all()
    serializer_class = RequestQuoteSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Request quotes retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "message": "Request quote retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
    
        try:
            self._send_admin_notification(serializer.data)
            print("Admin email sent successfully")
        except Exception as e:
            print(f"Email error — {type(e).__name__}: {e}") 
    
        return Response({
            "success": True,
            "message": "Request quote created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "message": "Request quote updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Request quote deleted successfully"
        }, status=status.HTTP_200_OK)

    def _send_admin_notification(self, data):
        subject = "New Quote Request Received"
    
        first_name = data.get('firstName') or data.get('first_name', '')
        last_name = data.get('lastName') or data.get('last_name', '')
        email = data.get('email', '')
        phone = data.get('phone', '')
        company = data.get('companyName') or data.get('company_name', '')
        interest = data.get('interest', '')
        description = data.get('description', '')
    
        text_message = f"""
    New Quote Request
    
    Name: {first_name} {last_name}
    Email: {email}
    Phone: {phone}
    Company: {company}
    Interest: {interest}
    Description: {description}
    """
    
        html_message = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>New Quote Request</title>
    </head>
    <body style="margin:0;padding:0;background-color:#0f0f0f;font-family:'Georgia',serif;">
    
      <!-- Outer wrapper -->
      <table width="100%" cellpadding="0" cellspacing="0" border="0"
             style="background-color:#0f0f0f;padding:48px 16px;">
        <tr>
          <td align="center">
    
            <!-- Card -->
            <table width="600" cellpadding="0" cellspacing="0" border="0"
                   style="max-width:600px;width:100%;background-color:#1a1a1a;
                          border-radius:2px;overflow:hidden;
                          border:1px solid #2a2a2a;">
    
              <!-- Top accent bar -->
              <tr>
                <td style="background:linear-gradient(90deg,#c8a96e 0%,#e8c97e 50%,#c8a96e 100%);
                           height:4px;font-size:0;line-height:0;">&nbsp;</td>
              </tr>
    
              <!-- Header -->
              <tr>
                <td style="padding:40px 48px 32px;border-bottom:1px solid #2a2a2a;">
                  <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td>
                        <!-- Logo / Brand mark -->
                        <div style="display:inline-block;background:linear-gradient(135deg,#c8a96e,#e8c97e);
                                    width:42px;height:42px;border-radius:2px;
                                    text-align:center;line-height:42px;
                                    font-size:20px;font-weight:bold;color:#0f0f0f;
                                    font-family:'Georgia',serif;margin-bottom:20px;">Q</div>
                        <p style="margin:0 0 6px;font-size:11px;letter-spacing:4px;
                                   color:#c8a96e;text-transform:uppercase;
                                   font-family:'Courier New',monospace;">Incoming Request</p>
                        <h1 style="margin:0;font-size:28px;font-weight:normal;
                                   color:#f5f0e8;letter-spacing:-0.5px;
                                   font-family:'Georgia',serif;line-height:1.2;">
                          New Quote Request
                        </h1>
                      </td>
                      <td align="right" valign="top" style="padding-top:4px;">
                        <p style="margin:0;font-size:11px;color:#555;
                                   font-family:'Courier New',monospace;letter-spacing:1px;">
                          ACTION REQUIRED
                        </p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
    
              <!-- Body -->
              <tr>
                <td style="padding:36px 48px;">
    
                  <!-- Intro line -->
                  <p style="margin:0 0 32px;font-size:14px;color:#888;
                             font-family:'Courier New',monospace;letter-spacing:1px;">
                    A new client has submitted a quote request. Details below.
                  </p>
    
                  <!-- Fields -->
                  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    
                    <!-- Name -->
                    <tr>
                      <td style="padding:0 0 20px;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0"
                               style="background-color:#222;border-left:3px solid #c8a96e;
                                      border-radius:0 2px 2px 0;">
                          <tr>
                            <td style="padding:16px 20px;">
                              <p style="margin:0 0 4px;font-size:10px;letter-spacing:3px;
                                         color:#c8a96e;text-transform:uppercase;
                                         font-family:'Courier New',monospace;">Full Name</p>
                              <p style="margin:0;font-size:17px;color:#f5f0e8;
                                         font-family:'Georgia',serif;">{first_name} {last_name}</p>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
    
                    <!-- Email + Phone (two columns) -->
                    <tr>
                      <td style="padding:0 0 20px;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                          <tr>
                            <!-- Email -->
                            <td width="48%" style="vertical-align:top;">
                              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                                     style="background-color:#222;border-left:3px solid #3a6e5a;
                                            border-radius:0 2px 2px 0;">
                                <tr>
                                  <td style="padding:16px 20px;">
                                    <p style="margin:0 0 4px;font-size:10px;letter-spacing:3px;
                                               color:#5aae8a;text-transform:uppercase;
                                               font-family:'Courier New',monospace;">Email</p>
                                    <p style="margin:0;font-size:14px;color:#f5f0e8;
                                               font-family:'Courier New',monospace;word-break:break-all;">
                                      <a href="mailto:{email}"
                                         style="color:#5aae8a;text-decoration:none;">{email}</a>
                                    </p>
                                  </td>
                                </tr>
                              </table>
                            </td>
    
                            <td width="4%"></td>
    
                            <!-- Phone -->
                            <td width="48%" style="vertical-align:top;">
                              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                                     style="background-color:#222;border-left:3px solid #3a6e5a;
                                            border-radius:0 2px 2px 0;">
                                <tr>
                                  <td style="padding:16px 20px;">
                                    <p style="margin:0 0 4px;font-size:10px;letter-spacing:3px;
                                               color:#5aae8a;text-transform:uppercase;
                                               font-family:'Courier New',monospace;">Phone</p>
                                    <p style="margin:0;font-size:14px;color:#f5f0e8;
                                               font-family:'Courier New',monospace;">{phone}</p>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
    
                    <!-- Company -->
                    <tr>
                      <td style="padding:0 0 20px;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0"
                               style="background-color:#222;border-left:3px solid #c8a96e;
                                      border-radius:0 2px 2px 0;">
                          <tr>
                            <td style="padding:16px 20px;">
                              <p style="margin:0 0 4px;font-size:10px;letter-spacing:3px;
                                         color:#c8a96e;text-transform:uppercase;
                                         font-family:'Courier New',monospace;">Company</p>
                              <p style="margin:0;font-size:17px;color:#f5f0e8;
                                         font-family:'Georgia',serif;">{company}</p>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
    
                    <!-- Interest -->
                    <tr>
                      <td style="padding:0 0 20px;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0"
                               style="background-color:#222;border-left:3px solid #6e3a6e;
                                      border-radius:0 2px 2px 0;">
                          <tr>
                            <td style="padding:16px 20px;">
                              <p style="margin:0 0 4px;font-size:10px;letter-spacing:3px;
                                         color:#b06eb0;text-transform:uppercase;
                                         font-family:'Courier New',monospace;">Area of Interest</p>
                              <p style="margin:0;font-size:17px;color:#f5f0e8;
                                         font-family:'Georgia',serif;">{interest}</p>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
    
                    <!-- Description -->
                    <tr>
                      <td style="padding:0 0 0;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0"
                               style="background-color:#1e1e1e;border:1px solid #2e2e2e;
                                      border-radius:2px;">
                          <tr>
                            <td style="padding:20px;">
                              <p style="margin:0 0 10px;font-size:10px;letter-spacing:3px;
                                         color:#888;text-transform:uppercase;
                                         font-family:'Courier New',monospace;">Description</p>
                              <p style="margin:0;font-size:15px;color:#ccc;
                                         font-family:'Georgia',serif;line-height:1.7;">
                                {description}
                              </p>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
    
                  </table>
    
                  <!-- CTA Button -->
                  <table width="100%" cellpadding="0" cellspacing="0" border="0"
                         style="margin-top:36px;">
                    <tr>
                      <td>
                        <a href="mailto:{email}"
                           style="display:inline-block;background:linear-gradient(135deg,#c8a96e,#e8c97e);
                                  color:#0f0f0f;text-decoration:none;
                                  padding:14px 32px;border-radius:2px;
                                  font-size:11px;letter-spacing:3px;text-transform:uppercase;
                                  font-family:'Courier New',monospace;font-weight:bold;">
                          Reply to Client
                        </a>
                      </td>
                    </tr>
                  </table>
    
                </td>
              </tr>
    
              <!-- Footer -->
              <tr>
                <td style="padding:24px 48px;border-top:1px solid #2a2a2a;
                           background-color:#141414;">
                  <p style="margin:0;font-size:11px;color:#444;
                             font-family:'Courier New',monospace;letter-spacing:1px;">
                    This is an automated notification. Do not reply to this email directly.<br/>
                    &copy; 2026 Techbridge Solution &mdash; Admin Notifications
                  </p>
                </td>
              </tr>
    
              <!-- Bottom accent bar -->
              <tr>
                <td style="background:linear-gradient(90deg,#c8a96e 0%,#e8c97e 50%,#c8a96e 100%);
                           height:2px;font-size:0;line-height:0;">&nbsp;</td>
              </tr>
    
            </table>
            <!-- /Card -->
    
          </td>
        </tr>
      </table>
    
    </body>
    </html>"""
    
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.ADMIN_EMAIL],
            reply_to=[email],
        )
    
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send(fail_silently=False)