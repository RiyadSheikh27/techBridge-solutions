from django.urls import path, include
from . import views
from product.views import *
from rest_framework.routers import DefaultRouter
from rest_framework import routers

router = DefaultRouter()

""" Registered ViewSets for Product Section """
router.register(r'products/categories', ProductCategoryViewSet, basename='category')
router.register(r'products/subcategories', ProductSubCategoryViewSet, basename='subcategory')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'products/category-descriptions', CategoryDescriptionViewSet, basename='category-description')
router.register(r'products/descriptions', ProductDescriptionViewSet, basename='product-description')
router.register(r'products/description-rows', ProductDescriptionRowViewSet, basename='description-row')


urlpatterns = [
    path('', include(router.urls)),
]