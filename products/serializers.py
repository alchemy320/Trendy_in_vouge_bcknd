from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

# class ProductSerializer(serializers.ModelSerializer):
#     category = CategorySerializer()  # Nesting the category inside product details

#     class Meta:
#         model = Product
#         fields = ['id', 'name', 'category', 'price', 'description', 'image', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields= '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'category',
            'price',
            'description',
            'image',
            'created_at'
        ]