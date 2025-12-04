import uuid
from django.db import models
from django.utils.text import slugify
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.utils import timezone


# Create your models here.
class TimeStampedModel(models.Model):
    """Abstract base model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class ProductCategory(TimeStampedModel):
    """ Categories for Model """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order for displaying categories"
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while ProductCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    @property
    def active_subcategories_count(self):
        return self.subcategories.filter(is_active=True).count()
      

class ProductSubCategory(TimeStampedModel):
    """
    Product subcategories under main categories
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE) 
    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order for displaying subcategories"
    )

    def __str__(self):
        return f"{self.category.name} - {self.name}"    

    class Meta:
        db_table = 'product_subcategories'
        verbose_name = 'Product Subcategory'
        verbose_name_plural = 'Product Subcategories'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['slug'])
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while ProductSubCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def active_products_count(self):
        return self.products.filter(is_active=True).count()


class CategoryDescription(TimeStampedModel):
    """ Product SubCategory Description """
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable=False)
    productSubCategory = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'product_subcategory_descriptions'
        verbose_name = 'Product Subcategory Description'
        verbose_name_plural = 'Product Subcategory Descriptions'
        ordering = ['id']

    
class Product(TimeStampedModel):
    """ Main product model with pricing """
    PRODUCT_TYPE = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subcategory = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=255, choices=PRODUCT_TYPE, default='hardware')
    name = models.CharField(max_length=510, blank=True, null=True)
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)
    series = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    msrp = models.DecimalField(max_digits=10, decimal_places=2, help_text="Main Price")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price after discount")
    stock = models.IntegerField(default=100)
    is_in_stock = models.BooleanField(default=True)
    mfr_part = models.CharField(max_length=255, null=True, blank=True, help_text="Manufacturer Part Number")
    shi_part = models.CharField(max_length=255, blank=True, null=True, help_text="Shipper Part Number")
    unspsc = models.CharField(max_length=255, null=True, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(help_text="Full product description (comma-separated for overview)")

    is_active = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    display_order = models.PositiveIntegerField(default=0,help_text="Display order")

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "products"
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subcategory', 'is_active']),
            models.Index(fields=['manufacturer', 'is_active']),
            models.Index(fields=['product_type', 'is_active']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    

    def get_overview(self):
        if self.description:
            items = [item.strip() for item in self.description.split(',') if item.strip()]
            return items
        return []
    

    
class ProductDescription(TimeStampedModel):
    """ Multiple Description Blocks for a Product """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Is this description block active?")
    display_order = models.PositiveIntegerField(default=0, help_text="Display order")

    def __str__(self):
        return f"{self.product.name} - {self.title}"
    
    class Meta:
        db_table = 'product_descriptions'
        verbose_name = 'Product Description'
        verbose_name_plural = 'Product Descriptions'
        ordering = ['display_order', 'id']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['display_order']),
        ]


class ProductDescriptionRow(TimeStampedModel):
    """ Key-value pairs for product description details """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.ForeignKey(ProductDescription, on_delete=models.CASCADE)
    key = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0, help_text="Display order")

    class Meta:
        db_table = 'product_description_rows'
        verbose_name = 'Product Description Row'
        verbose_name_plural = 'Product Description Rows'
        ordering = ['display_order', 'id']
        indexes = [
            models.Index(fields=['description', 'display_order']),
        ]

    def __str__(self):
        return f"{self.key}: {self.value}"

    def save(self, *args, **kwargs):
        if self.display_order == 0:
            last_order = ProductDescriptionRow.objects.filter(
                description=self.description
            ).aggregate(models.Max('display_order'))['display_order__max'] or 0
            self.display_order = last_order + 1
        super().save(*args, **kwargs)
