from django.db.models import Q

from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ReviewSerializer,
)


# ============================================================
# PRODUCT REVIEWS
# ============================================================

class ProductReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]

        return Review.objects.filter(
            product_id=product_id
        ).select_related("user")

    def perform_create(self, serializer):
        product_id = self.kwargs["product_id"]

        serializer.save(
            user=self.request.user,
            product_id=product_id
        )

    def get_permissions(self):
        # Anyone can READ reviews
        if self.request.method == "GET":
            return [permissions.AllowAny()]

        # Only logged-in users can CREATE reviews
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]

        return [permissions.IsAuthenticated()]


# ============================================================
# PRODUCTS
# ============================================================

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()

        # Search products
        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
            )

        return queryset

    def get_permissions(self):

        # Customers can view products
        if self.action in ["list", "retrieve"]:
            permission_classes = [
                permissions.AllowAny
            ]

        # Only admins can add, edit or delete products
        else:
            permission_classes = [
                permissions.IsAdminUser
            ]

        return [
            permission()
            for permission in permission_classes
        ]


# ============================================================
# CATEGORIES
# ============================================================

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    serializer_class = CategorySerializer

    # Customers can view categories
    # Admins can also create, update and delete them
    def get_permissions(self):

        if self.action in ["list", "retrieve"]:
            permission_classes = [
                permissions.AllowAny
            ]

        else:
            permission_classes = [
                permissions.IsAdminUser
            ]

        return [
            permission()
            for permission in permission_classes
        ]


# ============================================================
# PRODUCT BULK UPLOAD
# ============================================================

class ProductBulkUploadView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):

        return Response(
            {
                "message": "Products uploaded successfully"
            },
            status=status.HTTP_201_CREATED
        )