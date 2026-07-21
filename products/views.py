from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductBulkUploadView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        data=request.data
        return Response({'message': 'Products uploaded successfully'}, status=status.HTTP_201_CREATED)
