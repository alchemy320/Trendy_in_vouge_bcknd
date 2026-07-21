from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from .views import ProductBulkUploadView, CategoryViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'catogory', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('products/bulk/', ProductBulkUploadView.as_view(), name='product-bulk-upload'),
]