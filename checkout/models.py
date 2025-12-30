from django.db import models
import uuid
from decimal import Decimal
from product.models import TimeStampedModel, Product
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from authentication.models import Users

""" Start of Creating Models for Checkout Section """

class Cart(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'cart'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active'])
        ]

    def __str__(self):
        return f"Cart {self.id}"

    @property
    def subtotal(self):
        """Subtotal of cart items"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        """Total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    def calculate_total(self, delivery_charge=Decimal('0.00')):
        """Calculate cart total with delivery charge"""
        return self.subtotal + delivery_charge


class CartItem(TimeStampedModel):
    """Individual items in shopping cart"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Price at the time of adding to cart"
    )
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ['-created_at']
        unique_together = [['cart', 'product']]
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.price * self.quantity
    
    
    def save(self, *args, **kwargs):
        if self.price is None or self.price == Decimal("0.00"):
            self.price = self.product.price
        super().save(*args, **kwargs)


class Order(TimeStampedModel):
    """ Customer Order Model """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=100, unique=True, db_index=True)
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    
    first_name = models.CharField(max_length=255,blank=True, null=True)
    last_name = models.CharField(max_length=255,blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20,blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2,default=Decimal('0.00'))

    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True
    )
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status', 'payment_status']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        """Generate order number if not set"""
        if not self.order_number:
            import random
            import string
            from django.utils import timezone
            
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_str = ''.join(random.choices(string.digits, k=4))
            self.order_number = f"ORD-{timestamp}-{random_str}"
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """Get customer full name"""
        return f"{self.first_name} {self.last_name}"

class OrderItem(TimeStampedModel):
    """ Order Item Model """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['id']
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def total_price(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        """Calculate total if not set"""
        if not self.total:
            self.total = self.price * self.quantity
        if not self.product_name and self.product:
            self.product_name = self.product.name
        super().save(*args, **kwargs)


class DeliveryCharge(TimeStampedModel):
    """Global delivery charge settings"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('10.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'delivery_charges'
        verbose_name = 'Delivery Charge'
        verbose_name_plural = 'Delivery Charges'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"${self.amount}"
    
    @classmethod
    def get_current_charge(cls):
        """Get current active delivery charge"""
        charge = cls.objects.filter(is_active=True).first()
        return charge.amount if charge else Decimal('10.00')

class ProductReview(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}✯"

    class Meta:
        verbose_name = 'product_review'
        verbose_name_plural = 'product_reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]
