from django.contrib import admin
from .models import *

""" Registering Models for Checkout Section """
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(DeliveryCharge)
