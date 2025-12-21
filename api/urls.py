from django.urls import path, include
from . import views
from product.views import *
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from django.contrib import admin
from .swagger import schema_view
from checkout.views import *


router = DefaultRouter()

""" Registered ViewSets for Product Section """
router.register(r'products/categories', ProductCategoryViewSet, basename='category')
router.register(r'products/subcategories', ProductSubCategoryViewSet, basename='subcategory')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'products-subcategory-descriptions', CategoryDescriptionViewSet, basename='subcategory-description')
router.register(r'products-descriptions', ProductDescriptionViewSet, basename='product-description')
router.register(r'products-description-rows', ProductDescriptionRowViewSet, basename='description-row')



""" Registered ViewSets for Delivery Charge Section """
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'delivery-charge', DeliveryChargeViewSet, basename='delivery-charge')

""" Registered ViewSets for Checkout Section """
router.register(r'cart', CartViewSet, basename='cart')


urlpatterns = [
    path('', include(router.urls)),
    path('checkout/create-payment-intent/', CheckoutViewSet.as_view({'post': 'create_payment_intent'}), name='create-payment-intent'),
    path('checkout/confirm-payment/', CheckoutViewSet.as_view({'post': 'confirm_payment'}), name='confirm-payment'),
    path('checkout/create-order/', CheckoutViewSet.as_view({'post': 'create_order'}), name='create-order'),
    
    path('swagger/', schema_view.with_ui('swagger',cache_timeout=0), name='schema-swagger-ui'),
]