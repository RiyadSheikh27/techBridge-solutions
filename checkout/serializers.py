from rest_framework import serializers
from .models import *
from product.models import Product

""" Start of Serializers for Checkout Section """

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for Cart Item"""
    product_name = serializers.CharField(source='product.name')
    product_image = serializers.ImageField(source='product.image')
    product_image_url = serializers.URLField(source='product.image_url')
    product_slug = serializers.CharField(source='product.slug')
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    msrp = serializers.DecimalField(max_digits=10, decimal_places=2, source='product.msrp', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'cart', 'product_name', 'product_image', 'product_image_url', 'product_slug', 'quantity', 'price', 'total_price', 'msrp', 'created_at', 'updated_at']
        read_only_fields = ['id', 'price', 'created_at', 'updated_at', 'msrp']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return value

    def validate_product(self, value):
        if not value.is_active:
            raise serializers.ValidationError('Product is not active')
        if not value.is_in_stock:
            raise serializers.ValidationError('Product is out of stock')
        return value

class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart"""
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    delivery_charge = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'subtotal', 'delivery_charge', 'total', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_delivery_charge(self, obj):
        """Get current delivery charge"""
        return str(DeliveryCharge.get_current_charge())
    
    def get_total(self, obj):
        """Calculate total with delivery charge"""
        delivery = DeliveryCharge.get_current_charge()
        return str(obj.calculate_total(delivery))

    def get_delivery_charge(self, obj):
        """Get current delivery charge"""
        return str(DeliveryCharge.get_current_charge())


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(default=1, min_value=1)
    
    def validate_product_id(self, value):
        """Validate product exists and is available"""
        try:
            product = Product.objects.get(id=value)
            if not product.is_active:
                raise serializers.ValidationError("Product is not available")
            if not product.is_in_stock:
                raise serializers.ValidationError("Product is out of stock")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    cart_item_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for Order Item"""
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 
            'quantity', 'price', 'total'
        ]

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders with items"""
    items = OrderItemSerializer(many=True, read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'first_name', 'last_name',
            'full_name', 'company_name', 'email', 'phone', 
            'address', 'subtotal', 'delivery_charge', 'total',
            'status', 'payment_status', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'payment_status',
            'created_at', 'updated_at'
        ]

class MyOrdersSerializer(serializers.ModelSerializer):
    """Serializer for my orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'subtotal', 'delivery_charge', 'total',
            'status', 'payment_status', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'payment_status',
            'created_at', 'updated_at'
        ]

class CheckoutSerializer(serializers.Serializer):
    """Serializer for checkout process"""
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    company_name = serializers.CharField(
        max_length=255, 
        required=False, 
        allow_blank=True
    )
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    
    def validate_email(self, value):
        """Validate email format"""
        return value.lower()
    
    def validate_phone(self, value):
        """Validate phone number"""
        cleaned = ''.join(filter(str.isdigit, value))
        if len(cleaned) < 10:
            raise serializers.ValidationError(
                "Phone number must be at least 10 digits"
            )
        return value

class DeliveryChargeSerializer(serializers.ModelSerializer):
    """Serializer for delivery charge"""
    
    class Meta:
        model = DeliveryCharge
        fields = ['id', 'amount', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']