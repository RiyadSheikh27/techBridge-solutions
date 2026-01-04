import stripe
from django.shortcuts import render
from rest_framework import viewsets, status
from .models import *
from .serializers import *
from product.views import CustomResponseMixin
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from product.models import Product
from authentication.permissions import IsAdmin, IsAdminOrReadOnly
from django.db import transaction

stripe.api_key = settings.STRIPE_SECRET_KEY

""" Start of Views for Checkout Section """

class CartViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for shopping cart operations
    
    list: Get current cart with all items
    add_item: Add product to cart
    update_item: Update item quantity
    remove_item: Remove item from cart
    clear: Clear entire cart
    """
    permission_class = [IsAuthenticatedOrReadOnly]

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

class OrderViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for orders (read-only)
    
    list: Get orders (admin: all, user: own orders)
    retrieve: Get single order details
    update_status: Update order status (admin only)
    my_orders: Get current user's orders (authenticated users)
    track_order: Track order by order number and email (public)
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_number'
    
    def get_queryset(self):
        """Get orders based on user role"""
        queryset = Order.objects.prefetch_related('items').all()
        
        """Admin sees all orders"""
        if self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.is_superuser
        ):
            return queryset.order_by('-created_at')
        

        """Authenticate users sees their own orders"""
        if self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user).order_by('-created_at')

        """Regular users filter by email"""
        email = self.request.query_params.get('email', None)
        if email:
            queryset = queryset.filter(email=email.lower())
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        """pagination"""
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message="Orders retrieved successfully"
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return self.success_response(
            data=serializer.data,
            message="Order retrieved successfully"
        )

    @action(detail=True, methods=['patch'])
    def update_status(self, request, order_number=None):
        """Update order status (admin only)"""
        if not request.user.is_authenticated or not request.user.is_staff:
            return self.error_response(
                message="Admin access required",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        
        if not new_status:
            return self.error_response(
                message="Status is required"
            )
        
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        if new_status not in valid_statuses:
            return self.error_response(
                message=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        try:
            order = self.get_object()
            old_status = order.status
            order.status = new_status
            
            """Auto-update payment status based on order status"""
            if new_status == 'completed':
                order.payment_status = 'completed'
            elif new_status == 'failed' or new_status == 'cancelled':
                if order.payment_status == 'pending':
                    order.payment_status = 'failed'
            
            order.save()
            serializer = self.get_serializer(order)
            
            return self.success_response(
                data=serializer.data,
                message=f"Order status updated from {old_status} to {new_status}"
            )
            
        except Exception as e:
            return self.error_response(
                message=f"Failed to update status: {str(e)}"
            )

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """ get current user's orders (authenticated users)"""
        if not request.user.is_authenticated:
            return self.error_response(
                message = "Authentication required",
                status_code = status.HTTP_401_UNAUTHORIZED
            )
        
        orders = Order.objects.filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)

        return self.success_response(
            message="Orders retrieved successfully",
            data=serializer.data
        )


    @action(detail=False, methods=['post'])
    def track_order(self, request):
        """Track order by order number and email"""
        order_number = request.data.get('order_number')
        email = request.data.get('email')
        
        if not order_number or not email:
            return self.error_response(
                message="Order number and email are required"
            )
        
        try:
            order = Order.objects.prefetch_related('items').get(
                order_number=order_number,
                email=email.lower()
            )
            
            serializer = self.get_serializer(order)
            
            return self.success_response(
                data=serializer.data,
                message="Order found successfully"
            )
            
        except Order.DoesNotExist:
            return self.error_response(
                message="Order not found. Please check your order number and email.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to track order: {str(e)}"
            )


class CheckoutViewSet(CustomResponseMixin, viewsets.ViewSet):
    """
    ViewSet for checkout and payment operations
    
    Best Practice Flow:
    1. create_order: Create order with customer info (status: pending)
    2. create_payment_intent: Create Stripe payment intent with order_id
    3. confirm_payment: Verify payment and update order status to paid
    """

    permission_classes = [IsAuthenticated]

    def get_cart(self, request):
        """Get user's cart """
        try:
            return Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return None
            
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """Create order with customer information"""
        checkout_serializer = CheckoutSerializer(data=request.data)
        if not checkout_serializer.is_valid():
            return self.error_response(
                message="Validation failed",
                errors=checkout_serializer.errors
            )
        
        """Get cart"""
        cart = self.get_cart(request)
        if not cart or not cart.items.exists():
            return self.error_response(
                message="Cart is empty",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            """Create order with transaction"""
            with transaction.atomic():
                delivery_charge = DeliveryCharge.get_current_charge()
                subtotal = cart.subtotal
                total = cart.calculate_total(delivery_charge)
                
                """Create order with pending status"""
                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    first_name=checkout_serializer.validated_data['first_name'],
                    last_name=checkout_serializer.validated_data['last_name'],
                    company_name=checkout_serializer.validated_data.get('company_name', ''),
                    email=checkout_serializer.validated_data['email'],
                    phone=checkout_serializer.validated_data['phone'],
                    address=checkout_serializer.validated_data['address'],
                    subtotal=subtotal,
                    delivery_charge=delivery_charge,
                    total=total,
                    status='pending',
                    payment_status='pending'
                )
                
                """Create order items"""
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        product_name=cart_item.product.name,
                        quantity=cart_item.quantity,
                        price=cart_item.price,
                        total=cart_item.total_price
                    )
            
            """Serialize and return order"""
            order_serializer = OrderSerializer(order)
            
            return self.success_response(
                data=order_serializer.data,
                message="Order created successfully",
                status_code=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return self.error_response(
                message=f"Failed to create order: {str(e)}"
            )

    @action(detail=False, method=['post'])
    def create_payment_intent(self, request):
        """Create payment intent for order"""
        order_id = request.data.get('order_id')

        if not order_id:
            return self.error_response(
                message="Order ID is required"
            )
        
        try:
            order = Order.objects.get(id=order_id, payment_status='pending')
            
            intent = stripe.PaymentIntent.create(
                amount = int(order.total * 100),
                currency = 'usd',
                metadata = {
                    'order_id': str(order.id),
                    'order_number': order.order_number,
                    'email': order.email,
                    }
            )

            order.stripe_payment_intent_id = intent.id
            order.save()

            payment_data = {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': order.total,
                'currency': 'usd',
                'order_number': order.order_number,
            }

            return self.success_response(
                data=payment_data,
                message="Payment intent created successfully",
                status_code=status.HTTP_201_CREATED
            )
            
        except Order.DoesNotExist:
            return self.error_response(
                message="Order not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except stripe.error.StripeError as e:
            return self.error_response(
                message=f"Stripe error: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to create payment intent: {str(e)}"
            )
    
    @action(detail=False, methods=['post'])
    def confirm_payment(self, request):
        """Confirm payment and update order"""
        payment_intent_id = request.data.get('payment_intent_id')
        
        if not payment_intent_id:
            return self.error_response(
                message="Payment intent ID is required"
            )
        
        try:
            """Retrieve payment intent from Stripe to verify it succeeded"""
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status != 'succeeded':
                return self.error_response(
                    message=f"Payment not completed. Status: {intent.status}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            """Update order using the payment_intent_id stored in the order"""
            with transaction.atomic():
                order = Order.objects.select_for_update().get(
                    stripe_payment_intent_id=payment_intent_id
                )
                
                """Prevent duplicate confirmation"""
                if order.payment_status == 'completed':
                    return self.error_response(
                        message="Payment already confirmed",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                order.status = 'processing'
                order.payment_status = 'completed'
                order.save()
                
                """Clear the user's cart after successful payment"""
                if order.user:
                    cart = Cart.objects.filter(user=order.user, is_active=True).first()
                    if cart:
                        cart.items.all().delete()
            
            """Serialize order data to return"""
            order_serializer = OrderSerializer(order)
            
            return self.success_response(
                data=order_serializer.data,
                message="Payment confirmed successfully",
                status_code=status.HTTP_200_OK
            )
    
        except Order.DoesNotExist:
            return self.error_response(
                message="Order not found for this payment intent",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except stripe.error.InvalidRequestError as e:
            return self.error_response(
                message=f"Invalid payment intent: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except stripe.error.StripeError as e:
            return self.error_response(
                message=f"Stripe error: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return self.error_response(
                message=f"Failed to confirm payment: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class DeliveryChargeViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for delivery charges (read-only for customers)
    
    list: Get all delivery charges
    current: Get current active delivery charge
    """
    queryset = DeliveryCharge.objects.all()
    serializer_class = DeliveryChargeSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message="Delivery charges retrieved successfully"
        )

    def create(self, request, *args, **kwargs):
        """ Create Delivery Charge"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return self.success_response(
            data=serializer.data,
            message="Delivery charge created successfully"
        )

    def update(self, request, *args, **kwargs):
        """ Update Delivery Charge"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return self.success_response(
            data=serializer.data,
            message="Delivery charge updated successfully"
        )

    def destroy(self, request, *args, **kwargs):
        """ Delete Delivery Charge"""
        self.perform_destroy(self.get_object())
        
        return self.success_response(
            message="Delivery charge deleted successfully"
        )
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active delivery charge"""
        charge = DeliveryCharge.get_current_charge()
        
        return self.success_response(
            data={'amount': str(charge)},
            message="Current delivery charge retrieved successfully"
        )