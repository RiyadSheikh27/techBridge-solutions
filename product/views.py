import openpyxl
import uuid
from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from openpyxl import load_workbook
from io import BytesIO
from django.core.cache import cache


""" Start of Creating Views for Product Section """

class CustomResponseMixin:
    """Custom response mixin for API responses"""
    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        return Response({
            "success": True,
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
    permission_classes = [IsAuthenticatedOrReadOnly]
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

        product_type = self.request.query_params.get('product_type', None)
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        
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
            errors=serializere.rrors
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
    permission_classes = [IsAuthenticatedOrReadOnly]
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
    permission_classes = [IsAuthenticatedOrReadOnly]
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

    list: Get all category descriptions
    retrieve: Get a single category description
    create: Create a new category description
    update: Update a category description
    partial_update: Partially update a category description
    destroy: Delete a category description
    """
    queryset = CategoryDescription.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryDescriptionWriteSerializer
        return CategoryDescriptionSerializer

    def get_queryset(self):
        queryset = CategoryDescription.objects.all()
    
        subcategory_slug = self.request.query_params.get('subcategory', None)
        if subcategory_slug:
            queryset = queryset.filter(productSubCategory__slug=subcategory_slug)
    
        return queryset
    
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Category description updated successfully"
            )
        return self.error_response(
            message="Validation failed",
            errors=serializer.errors
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Category description partially updated successfully"
            )
        return self.error_response(
            message="Validation failed",
            errors=serializer.errors
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return self.success_response(
            message="Category description deleted successfully",
            status_code=204
        )

class ProductDescriptionViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for Product Descriptions

    list: Get all product descriptions
    retrieve: Get a single product description
    create: Create a new product description
    update: Update a product description
    partial_update: Partially update a product description
    destroy: Delete a product description
    """
    queryset = ProductDescription.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data = serializer.data,
                message = "Product Description Updated Successfully"
            )
        return self.error_response(
            message = "Validation failed",
            errors = serializer.errors
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data = serializer.data,
                message = "Product Description Updated Successfully"
            )
        return self.error_response(
            message = "Validation failed",
            errors = serializer.errors
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        return self.success_response(
            message="Category Description Deleted Sucessfully",
            status_code=204
        )



class ProductDescriptionRowViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for Product Description Rows

    list: Get all product description rows
    retrieve: Get a single product description row
    create: Create a new product description row
    update: Update a product description row
    partial_update: Partially update a product description row
    destroy: Delete a product description row
    """
    queryset = ProductDescriptionRow.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data = serializer.data,
                message="Product Description Updated Successfully"
            )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data = serializer.data,
                message="Product Description Updated Successfully"
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return self.success_response(
            status_code=204,
            message="Product Description Row Deleted Successfully"
        )


""" Bulk Product Upload from Excel Section """
class BulkProductUploadViewSet(CustomResponseMixin, viewsets.ViewSet):
    """ViewSet for Bulk Product Upload from Excel
    Upload Excel File to upload products
    Save Selected Products to Database
    """
    def _safe_decimal(self, value):
        """Safe Decimal Conversion"""
        if value is None or value == '':
            return Decimal(default)
        try:
            return Decimal(str(value))
        except ValueError:
            return Decimal(default)

    def _safe_int(self, value, default=0):
        """Safely convert value to integer"""
        if value is None or value == '':
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def _safe_bool(self, value, default=True):
        """Safely convert value to boolean"""
        if value is None or value == '':
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', 'yes', '1', 'y']
        return bool(value)

    def _parse_excel_row(self, row, subcategory_id, row_number):
        """Parse a single row from the Excel file"""
        try:
            """Generate unique id for this parsed product"""
            temp_id = str(uuid.uuid4())

            product_data = {
                'id': temp_id,
                'row_number': row_number,
                'subcategory': subcategory_id,
                'name': str(row[1].value or '').strip(),
                'series': str(row[2].value or '').strip() if row[2].value else None,
                'msrp': str(self._safe_decimal(row[3].value, '0.00')),
                'price': str(self._safe_decimal(row[4].value, '0.00')),
                'stock': self._safe_int(row[5].value, 100),
                'is_in_stock': self._safe_bool(row[6].value, True),
                'mfr_part': str(row[7].value or '').strip() if row[7].value else None,
                'shi_part': str(row[8].value or '').strip() if row[8].value else None,
                'unspsc': str(row[9].value or '').strip() if row[9].value else None,
                'manufacturer': str(row[10].value or '').strip() if row[10].value else None,
                'description': str(row[11].value or '').strip(),
                'is_active': self._safe_bool(row[12].value, False),
                'is_featured': self._safe_bool(row[13].value, False),
                'display_order': self._safe_int(row[14].value, 0),
                'valid': True,
                'errors': []
            }
            """Validate"""
            if not product_data['name']:
                product_data['valid'] = False
                product_data['errors'].append('Name is required')

            if not product_data['msrp']:
                product_data['valid'] = False
                product_data['errors'].append('MSRP is required')

            if not product_data['price']:
                product_data['valid'] = False
                product_data['errors'].append('Price is required')

            if not product_data['description']:
                product_data['valid'] = False
                product_data['errors'].append('Description is required')

            return product_data

        except Exception as e:
            return {
                'id': str(uuid.uuid4()),
                'row_number': row_number,
                'valid': False,
                'errors': [f'Error parsing row: {str(e)}'],
                'name': 'Error'
            }
    
    @action(detail=False, methods=['post'])
    def upload_excel(self, request):
        """
        Upload Excel file and get parsed products with unique IDs
        Expected request:
        - subcategory (UUID): Subcategory ID
        - file (File): Excel file
        """
        subcategory_id = request.data.get('subcategory')
        excel_file = request.data.get('file')

        if not subcategory_id:
            return self.error_response(
                message="Subcategory ID is required"
            )
        
        if not excel_file:
            return self.error_response(
                message="Excel file is required"
            )
        """Validate Subcategory exists"""
        try:
            subcategory = ProductSubCategory.objects.get(id=subcategory_id)
        except ProductSubCategory.DoesNotExist:
            return self.error_response(
                message="Subcategory does not exist",
                status_code=status.HTTP_404_NOT_FOUND
            )
        try:
            """Read Excel file"""
            workbook = openpyxl.load_workbook(BytesIO(excel_file.read()))
            sheet = workbook.active
            
            """Parse products (skip header row)"""
            products = []
            for idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
                """Skip empty rows"""
                if not any(cell.value for cell in row):
                    continue
                
                product_data = self._parse_excel_row(row, subcategory_id, idx)
                products.append(product_data)
            
            if not products:
                return self.error_response(
                    message="No valid products found in Excel file"
                )

            """ Store Products in Cache for Later Retrieval (30 minutes)"""
            cache_key = f"bulk_upload_{request.user.id}_{uuid.uuid4()}"
            cache.set(cache_key, products, timeout=1800)

            """Summary"""
            valid_count = sum(1 for p in products if p['valid'])
            invalid_count = len(products) - valid_count

            return self.success_response(
                data={
                    'cache_key': cache_key,
                    'subcategory': {
                        'id': str(subcategory.id),
                        'name': subcategory.name,
                        'category_name': subcategory.category.name
                    },
                    'products': products,
                    'summary': {
                        'total': len(products),
                        'valid': valid_count,
                        'invalid': invalid_count
                    }
                },
                message=f"Excel parsed successfully. {valid_count} valid products found."
            )
            
        except openpyxl.utils.exceptions.InvalidFileException:
            return self.error_response(
                message="Invalid Excel file format. Please upload a valid .xlsx file"
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to parse Excel file: {str(e)}"
            )
    

""" End ofBulk Product Upload from Excel Section """

""" End of Creating Views for Product Section """
