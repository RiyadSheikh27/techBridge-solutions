from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action

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
        return self.success_response(
            data=serializer.data,
            message="Category Listed Successfully"
            )

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
        serializer = self.get_serializer(instance, data=request.data, partial=True)
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

class ProductSubCategoryViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for Product SubCategories
    
    list: Get all subcategories with products
    retrieve: Get a single subcategory with all details
    create: Create a new subcategory
    update: Update a subcategory
    partial_update: Partially update a subcategory
    destroy: Delete a subcategory
    by_category: Get subcategories filtered by category slug
    """
    queryset = ProductSubCategory.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductSubCategoryWriteSerializer
        return ProductSubCategorySerializer

    def get_queryset(self):
        queryset = ProductSubCategory.objects.all()
        
        """ Filter by category """
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        """ Filter by active status """
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('display_order', 'name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Subcategories retrieved successfully"
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(
            data=serializer.data,
            message="Subcategory retrieved successfully"
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Subcategory created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Validation failed",
            errors=serializer.errors
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Subcategory updated successfully"
            )
        return self.error_response(
            message="Validation failed",
            errors=serializer.errors
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return self.success_response(
            message="Subcategory deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )

class ProductViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for Products
    
    list: Get all products
    retrieve: Get a single product with full details
    create: Create a new product
    update: Update a product
    partial_update: Partially update a product
    destroy: Delete a product
    by_type: Get products grouped by product type
    by_subcategory: Get products by subcategory slug
    featured: Get featured products
    """
    queryset = Product.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductWriteSerializer
        elif self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related(
            'subcategory',
            'subcategory__category'
        ).prefetch_related(
            'productdescription_set',
            'productdescription_set__productdescriptionrow_set'
        )
        """Filter by product type"""
        product_type = self.request.query_params.get('type', None)
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        
        """Filter by subcategory"""
        subcategory_slug = self.request.query_params.get('subcategory', None)
        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)
        
        """Filter by category"""
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(subcategory__category__slug=category_slug)
        
        """Filter by active status"""
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        """Filter by featured"""
        is_featured = self.request.query_params.get('is_featured', None)
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')
        
        """Search by name or manufacturer"""
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(manufacturer__icontains=search) |
                Q(mfr_part__icontains=search)
            )
        
        return queryset.order_by('display_order', '-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Products retrieved successfully"
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(
            data=serializer.data,
            message="Product retrieved successfully"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Product created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Validation failed",
            errors=serializer.errors
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Product updated successfully"
            )
        return self.error_response(
            message="Validation failed",
            errors=serializer.errors
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return self.success_response(
            message="Product deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get all products grouped by product type (hardware/software)"""
        product_type = request.query_params.get('type')
        if not product_type:
            return self.error_response(
                message="Product type parameter is required (hardware or software)"
            )
        
        if product_type not in ['hardware', 'software']:
            return self.error_response(
                message="Invalid product type. Must be 'hardware' or 'software'"
            )

        """ Get all active categories with products of this type"""
        categories = ProductCategory.objects.filter(
            is_active=True,
            productsubcategory__product__product_type=product_type,
            productsubcategory__product__is_active=True
        ).distinct().order_by('display_order', 'name')
        
        serializer = ProductCategorySerializer(categories, many=True)
        
        response_data = {
            'product_type': product_type,
            'categories': serializer.data
        }
        
        return self.success_response(
            data=response_data,
            message=f"{product_type.capitalize()} products retrieved successfully"
        )
    @action(detail=False, methods=['get'])
    def by_subcategory(self, request):
        """Get products by subcategory slug"""
        subcategory_slug = request.query_params.get('slug')
        if not subcategory_slug:
            return self.error_response(
                message="Subcategory slug is required"
            )
        
        products = self.get_queryset().filter(
            subcategory__slug=subcategory_slug
        )
        serializer = ProductDetailSerializer(products, many=True)
        return self.success_response(
            data=serializer.data,
            message="Products retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        products = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(products, many=True)
        return self.success_response(
            data=serializer.data,
            message="Featured products retrieved successfully"
        )

class CategoryDescriptionViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for Category Descriptions
    """
    queryset = CategoryDescription.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryDescriptionWriteSerializer
        return CategoryDescriptionSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Category descriptions retrieved successfully"
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Category description created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Validation failed",
            errors=serializer.errors
        )


class ProductDescriptionViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for Product Descriptions
    """
    queryset = ProductDescription.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductDescriptionWriteSerializer
        return ProductDescriptionSerializer
    
    def get_queryset(self):
        queryset = ProductDescription.objects.all()
        
        """Filter by product"""
        product_slug = self.request.query_params.get('product', None)
        if product_slug:
            queryset = queryset.filter(product__slug=product_slug)
        
        return queryset.order_by('display_order')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Product descriptions retrieved successfully"
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Product description created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Validation failed",
            errors=serializer.errors
        )


class ProductDescriptionRowViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for Product Description Rows
    """
    queryset = ProductDescriptionRow.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductDescriptionRowWriteSerializer
        return ProductDescriptionRowSerializer
    
    def get_queryset(self):
        queryset = ProductDescriptionRow.objects.all()
        
        """Filter by description"""
        description_id = self.request.query_params.get('description', None)
        if description_id:
            queryset = queryset.filter(description__id=description_id)
        
        return queryset.order_by('display_order')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Product description rows retrieved successfully"
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Product description row created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Validation failed",
            errors=serializer.errors
        )

""" End of Creating Views for Product Section """
