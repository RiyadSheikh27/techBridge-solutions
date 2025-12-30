from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
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
        return Response({
            "success": True,
            "message": "Contact info created successfully",
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
    permission_classes = [IsAuthenticatedOrReadOnly]

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

        self._send_admin_notification(serializer.data)

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

    text_message = f"""
New Quote Request

Name: {data['firstName']} {data['lastName']}
Email: {data['email']}
Phone: {data['phone']}
Company: {data['companyName']}
Interest: {data['interest']}
Description: {data['description']}
"""

    html_message = f"""
    <h2>New Quote Request</h2>
    <p><strong>Name:</strong> {data['firstName']} {data['lastName']}</p>
    <p><strong>Email:</strong> {data['email']}</p>
    <p><strong>Phone:</strong> {data['phone']}</p>
    <p><strong>Company:</strong> {data['companyName']}</p>
    <p><strong>Interest:</strong> {data['interest']}</p>
    <p><strong>Description:</strong> {data['description']}</p>
    """

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.ADMIN_EMAIL],
        reply_to=[data['email']], 
    )

    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)
