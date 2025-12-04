from django.contrib import admin
from django.contrib.admin import register
from .models import *

# Register your models here.
admin.site.register(ProductCategory)
admin.site.register(ProductSubCategory)
admin.site.register(CategoryDescription)
admin.site.register(Product)
admin.site.register(ProductDescription)
admin.site.register(ProductDescriptionRow)