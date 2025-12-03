import uuid
from django.db import models
from django.utils.text import slugify

# Create your models here.
class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid5, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_save=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductSubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid5, editable=False)
    productCategory = models.ForeignKey(ProductCategory, on_delete=models.CASCADE) 
    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_save=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductSubSubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid5, editable=False)
    productSubCategory = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_save=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class CategoryDescription(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid5, editable=False)
    ProductSubSubCategory = models.ForeignKey(ProductSubSubCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Product(models.Model):
    PRODUCT_TYPE = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid5, editable=False)
    ProductSubSubCategory = models.ForeignKey(ProductSubSubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=510, blank=True, null=True)
    series = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='product', blank=True, null=True)
    msrp = models.models.DecimalField(max_digits=10, decimal_places=2, help_text="Main Price")
    price = models.models.DecimalField(max_digits=10, decimal_places=2, help_text="Price after discount")
    stock = models.IntegerField(default=100)
    is_in_stock = models.BooleanField(default=True)
    mfr_part = models.CharField(max_length=255, null=True, blank=True)
    shi_part = models.CharField(max_length=255, blank=True, null=True)
    unspsc = models.CharField(max_length=255, null=True, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    product_type = models.CharField(max_length=255, choices=PRODUCT_TYPE, default='hardware')
    description = models.TextField()

    def __str__(self):
        return self.name
    
class ProductDescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid5, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title
    
class ProductDescriptionRow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid5, editable=False)
    productDescription = models.ForeignKey(ProductDescription, on_delete=models.CASCADE)
    key = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.order == 0:
            last_order = ProductDescriptionRow.objects.filter(
                ProductDescription=self.productDescription
            ).aggregate(models.Max('order'))['order_max'] or 0

            self.order = last_order + 1

        super().save(*args, **kwargs)








