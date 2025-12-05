from django.urls import path
from . import views
from product.views import *
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from django.urls import include

router = DefaultRouter()
router.register(r'product-category', ProductCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]