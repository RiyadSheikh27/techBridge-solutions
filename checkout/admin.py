from django.contrib import admin
from django.utils.html import format_html
from .models import *


class CartItemInline(admin.TabularInline):
    """Inline for cart items"""
    model = CartItem
    extra = 0
    fields = ['product', 'quantity', 'price', 'total_price']
    readonly_fields = ['total_price']
    
    def total_price(self, obj):
        return f"${obj.total_price}"
    total_price.short_description = 'Total'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for shopping carts"""
    list_display = [
        'session_id_display', 'user', 'total_items',
        'subtotal_display', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['session_id', 'user__email', 'user__username']
    readonly_fields = ['session_id', 'subtotal', 'total_items', 'created_at', 'updated_at']
    inlines = [CartItemInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Cart Information', {
            'fields': ('session_id', 'user', 'is_active')
        }),
        ('Cart Summary', {
            'fields': ('total_items', 'subtotal')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def session_id_display(self, obj):
        """Display shortened session ID"""
        return obj.session_id[:20] + '...' if len(obj.session_id) > 20 else obj.session_id
    session_id_display.short_description = 'Session ID'
    
    def subtotal_display(self, obj):
        """Display formatted subtotal"""
        return format_html(
            '<strong style="color: green;">${}</strong>',
            obj.subtotal
        )
    subtotal_display.short_description = 'Subtotal'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin for cart items"""
    list_display = ['id', 'cart', 'product', 'quantity', 'price', 'total_display']
    list_filter = ['created_at']
    search_fields = ['product__name', 'cart__session_id']
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    
    def total_display(self, obj):
        """Display formatted total"""
        return f"${obj.total_price}"
    total_display.short_description = 'Total'


class OrderItemInline(admin.TabularInline):
    """Inline for order items"""
    model = OrderItem
    extra = 0
    fields = ['product_name', 'product_type', 'quantity', 'price', 'total']
    readonly_fields = ['product_name', 'product_type', 'quantity', 'price', 'total']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for orders"""
    list_display = [
        'order_number', 'full_name', 'email', 
        'total_display', 'status_display', 
        'payment_status_display', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = [
        'order_number', 'email', 'first_name', 
        'last_name', 'phone'
    ]
    readonly_fields = [
        'order_number', 'stripe_payment_intent_id', 
        'stripe_charge_id', 'created_at', 'updated_at'
    ]
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Customer Information', {
            'fields': (
                'first_name', 'last_name', 'company_name',
                'email', 'phone', 'address'
            )
        }),
        ('Order Summary', {
            'fields': ('subtotal', 'delivery_charge', 'total')
        }),
        ('Payment Details', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def total_display(self, obj):
        """Display formatted total"""
        return format_html(
            '<strong style="color: green;">${}</strong>',
            obj.total
        )
    total_display.short_description = 'Total'
    
    def status_display(self, obj):
        """Display colored status"""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def payment_status_display(self, obj):
        """Display colored payment status"""
        colors = {
            'pending': 'orange',
            'paid': 'green',
            'failed': 'red',
            'refunded': 'gray'
        }
        color = colors.get(obj.payment_status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_display.short_description = 'Payment Status'
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of orders"""
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for order items"""
    list_display = [
        'order', 'product_name', 'product_type',
        'quantity', 'price', 'total'
    ]
    list_filter = ['product_type', 'created_at']
    search_fields = ['product_name', 'order__order_number']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        """Prevent manual addition of order items"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of order items"""
        return False


@admin.register(DeliveryCharge)
class DeliveryChargeAdmin(admin.ModelAdmin):
    """Admin for delivery charges"""
    list_display = ['amount_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Delivery Charge Settings', {
            'fields': ('amount', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def amount_display(self, obj):
        """Display formatted amount"""
        return format_html(
            '<strong style="color: green; font-size: 14px;">${}</strong>',
            obj.amount
        )
    amount_display.short_description = 'Delivery Charge'