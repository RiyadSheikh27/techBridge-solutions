from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from product.views import CustomResponseMixin
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

""" Start of Views for Checkout Section """

class CartViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """ViewSet for Cart"""
    permission_class = [IsAuthenticated]

    queryset = Cart.objects.all()

    def get_or_create_cart(self, request):
        if not request.user.is_authenticated:
            return None
    
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        
        if not cart:
            cart = Cart.objects.create(user=request.user, is_active=True)
        
        return cart

    def list(self, request):
        cart = self.get_or_create_cart(request)
        serializer = CartSerializer(cart)

        return self.success_response(
            data=serializer.data,
            message="Cart retrieved successfully",
            status_code=200
        )

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        serializer = AddToCartSerializer(data=request.data)
        
        if not serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                errors=serializer.errors
            )
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            product = Product.objects.get(id=product_id)
            cart = self.get_or_create_cart(request)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={
                    'quantity': quantity,
                    'price': product.price
                }
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            cart_serializer = CartSerializer(cart)
            
            return self.success_response(
                data=cart_serializer.data,
                message=f"{product.name} added to cart successfully",
                status_code=status.HTTP_201_CREATED
            )
            
        except Product.DoesNotExist:
            return self.error_response(
                message="Product not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to add item to cart: {str(e)}"
            )

    @action(detail=False, methods=['patch'], url_path='update_item')
    def update_item(self, request):
        """Update cart item quantity"""
        serializer = UpdateCartItemSerializer(data=request.data)
        
        if not serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                errors=serializer.errors
            )
        
        cart_item_id = serializer.validated_data.get("cart_item_id")
        quantity = serializer.validated_data.get("quantity")
        
        try:
            cart = self.get_or_create_cart(request)
            if not cart:
                return self.error_response(
                    message="Cart not found", 
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            cart_item = CartItem.objects.filter(id=cart_item_id, cart=cart).first()
            if not cart_item:
                return self.error_response(
                    message="Cart item not found", 
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            cart_item.quantity = quantity
            cart_item.save()
            
            cart_serializer = CartSerializer(cart)
            return self.success_response(
                data=cart_serializer.data,
                message="Cart item updated successfully",
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return self.error_response(
                message=f"Failed to update cart item: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['delete'], url_path='remove_item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """Remove item from cart"""
        try:
            cart = self.get_or_create_cart(request)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            
            product_name = cart_item.product.name
            cart_item.delete()
            
            cart_serializer = CartSerializer(cart)
            
            return self.success_response(
                data=cart_serializer.data,
                message=f"{product_name} removed from cart"
            )
            
        except CartItem.DoesNotExist:
            return self.error_response(
                message="Cart item not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to remove item: {str(e)}"
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear entire cart"""
        try:
            cart = self.get_or_create_cart(request)
            cart.items.all().delete()
            
            cart_serializer = CartSerializer(cart)
            
            return self.success_response(
                data=cart_serializer.data,
                message="Cart cleared successfully"
            )
            
        except Exception as e:
            return self.error_response(
                message=f"Failed to clear cart: {str(e)}"
            )