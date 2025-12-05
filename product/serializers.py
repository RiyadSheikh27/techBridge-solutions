from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from product.models import ProductDescription

""" Start of Creating Serializer for Product Section """
class ProductDescriptionRowSerializer(serializers.ModelSerializer):
    """Serializer for product description key-value pairs"""
    
    class Meta:
        model = ProductDescriptionRow
        fields = ['id', 'key', 'value', 'display_order']
        read_only_fields = ['id']

class ProductDescriptionSerializer(serializers.ModelSerializer):
    """Serializer for product description blocks with rows"""
    rows = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductDescription
        fields = ['id', 'title', 'subtitle', 'is_active', 'display_order', 'rows']
        read_only_fields = ['id']

    def get_rows(self, obj):
        rows = ProductDescriptionRow.objects.filter(
            description=obj
        ).order_by('display_order')
        return ProductDescriptionRowSerializer(rows, many=True).data
    
class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listing"""
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'series', 'image', 'msrp', 
            'price', 'stock', 'is_in_stock', 'manufacturer',
            'is_featured', 'product_type'
        ]

class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual product with all relations"""
    overview = serializers.SerializerMethodField()
    descriptions = serializers.SerializerMethodField()
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    category_name = serializers.CharField(source='subcategory.category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'subcategory', 'subcategory_name', 'category_name',
            'product_type', 'name', 'slug', 'series', 'image',
            'msrp', 'price', 'stock', 'is_in_stock',
            'mfr_part', 'shi_part', 'unspsc', 'manufacturer',
            'description', 'is_active', 'is_featured',
            'display_order', 'overview', 'descriptions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_overview(self, obj):
        return obj.get_overview()
    
    def get_descriptions(self, obj):
        """Get all description blocks with their rows"""
        descriptions = ProductDescription.objects.filter(
            product=obj,
            is_active=True
        ).order_by('display_order')
        return ProductDescriptionSerializer(descriptions, many=True).data

class CategoryDescriptionSerializer(serializers.ModelSerializer):
    """Serializer for subcategory descriptions"""
    
    class Meta:
        model = CategoryDescription
        fields = ['id', 'title', 'description']
        read_only_fields = ['id']

class ProductSubCategorySerializer(serializers.ModelSerializer):
    """Serializer for subcategories with descriptions and products"""
    descriptions = CategoryDescriptionSerializer(
        source='categorydescription_set', 
        many=True, 
        read_only=True
    )
    products = serializers.SerializerMethodField()
    active_products_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ProductSubCategory
        fields = [
            'id', 'name', 'slug', 'is_active', 'display_order',
            'active_products_count', 'descriptions', 'products'
        ]
        read_only_fields = ['id', 'slug']
    
    def get_products(self, obj):
        """Get all active products under this subcategory"""
        products = Product.objects.filter(
            subcategory=obj,
            is_active=True
        ).order_by('display_order', '-created_at')
        
        # Use detailed serializer for nested products
        return ProductDetailSerializer(products, many=True).data
    
class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for categories with subcategories"""
    subcategories = serializers.SerializerMethodField()
    active_subcategories_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'is_active', 'display_order',
            'active_subcategories_count', 'subcategories'
        ]
        read_only_fields = ['id', 'slug']
    
    def get_subcategories(self, obj):
        """Get all active subcategories"""
        subcategories = ProductSubCategory.objects.filter(
            category=obj,
            is_active=True
        ).order_by('display_order', 'name')
        return ProductSubCategorySerializer(subcategories, many=True).data
    
class ProductTypeSerializer(serializers.Serializer):
    """Serializer for product type grouping"""
    product_type = serializers.CharField()
    categories = ProductCategorySerializer(many=True)


class ProductCategoryWriteSerializer(serializer.ModelSerializer):
    """Serializer for writing product categories"""
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug', 'is_active', 'display_order']
        read_only_fields = ['id', 'slug']

class ProductSubCategoryWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating subcategories"""
    
    class Meta:
        model = ProductSubCategory
        fields = ['id', 'category', 'name', 'is_active', 'display_order']
        read_only_fields = ['id']

class CategoryDescriptionWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating subcategory descriptions"""
    
    class Meta:
        model = CategoryDescription
        fields = ['id', 'productSubCategory', 'title', 'description']
        read_only_fields = ['id']

class ProductWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products"""
    
    class Meta:
        model = Product
        fields = [
            'id', 'subcategory', 'product_type', 'name', 'series',
            'image', 'msrp', 'price', 'stock', 'is_in_stock',
            'mfr_part', 'shi_part', 'unspsc', 'manufacturer',
            'description', 'is_active', 'is_featured', 'display_order'
        ]
        read_only_fields = ['id'] 

    def validate(self, data):
        """Validate price is less than or equal to MSRP"""
        if data.get('price') and data.get('msrp'):
            if data['price'] > data['msrp']:
                raise serializers.ValidationError(
                    "Price cannot be greater than MSRP"
                )
        return data

class ProductDescriptionWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating product descriptions"""
    
    class Meta:
        model = ProductDescription
        fields = [
            'id', 'product', 'title', 'subtitle', 
            'is_active', 'display_order'
        ]
        read_only_fields = ['id']

class ProductDescriptionRowWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating description rows"""
    
    class Meta:
        model = ProductDescriptionRow
        fields = ['id', 'description', 'key', 'value', 'display_order']
        read_only_fields = ['id']

""" End of Creating Serializer for Product Section """