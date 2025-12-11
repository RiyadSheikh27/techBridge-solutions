from .models import *
from django.contrib import admin

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(DeliveryCharge)