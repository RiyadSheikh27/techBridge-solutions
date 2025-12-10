from rest_framework import serializers
from .models import *
from .models import CartItem, OrderItem, DeliveryCharge, Order, Cart
from product.models import Product

""" Start of Serializers for Checkout Section """

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for Cart Item"""
    product_name = serializers.CharField(source='product.name')
    product_image = serializers.CharField(source='product.image')
    product_slug = serializers.CharField(source='product.slug')
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'cart', 'product_name', 'product_image', 'product_slug', 'quantity', 'price', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'price', 'created_at', 'updated_at']

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
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'subtotal', 'total', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']