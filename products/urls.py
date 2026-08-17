from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet,
    ProductBulkUploadView,
    CategoryViewSet,
    ProductReviewListCreateView,
)


# ============================================================
# API ROUTER
# ============================================================

router = DefaultRouter()

router.register(
    r"products",
    ProductViewSet,
    basename="product"
)

router.register(
    r"categories",
    CategoryViewSet,
    basename="category"
)


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [

    # Products and Categories
    path(
        "",
        include(router.urls)
    ),

    # Product Reviews
    path(
        "products/<int:product_id>/reviews/",
        ProductReviewListCreateView.as_view(),
        name="product-reviews",
    ),

    # Product Bulk Upload
    path(
        "products/bulk/",
        ProductBulkUploadView.as_view(),
        name="product-bulk-upload",
    ),
]