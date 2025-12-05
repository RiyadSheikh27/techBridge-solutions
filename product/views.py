from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

""" Start of Creating Views for Product Section """
class CustomResponseMixin:
    """Custom response mixin for API responses"""
    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        return Response({
            "status": True,
            "message": message,
            "data": data
        }, status=status_code)

    def error_response(self, message="Error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Standard error response format"""
        response_data = {
            'success': False,
            'message': message,
            'data': None
        }
        if errors:
            response_data['errors'] = errors
        return Response(response_data, status=status_code)

class ProductCategoryViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for Product Categories
    
    list: Get all categories with subcategories and products
    retrieve: Get a single category with all details
    create: Create a new category
    update: Update a category
    partial_update: Partially update a category
    destroy: Delete a category
    """
    queryset = ProductCategory.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCategoryWriteSerializer
        return ProductCategorySerializer
    
    def get_queryset(self):
        queryset = ProductCategory.objects.all()
        
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('display_order', 'name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(
            data=serializer.data,
            message="Category retrieved successfully"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data= request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Category created successfully",
                status_code = status.HTTP_201_CREATED
            )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Category updated successfully"
            )
        return self.error_response(
            message="Failed to update category",
            errors=serializer.errors
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return self.success_response(
            message="Category deleted successfully"
        )