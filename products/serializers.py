from rest_framework import serializers

from .models import Category, Product, Review


# ==========================================
# REVIEW SERIALIZER
# ==========================================

class ReviewSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = Review

        fields = [
            "id",
            "product",
            "user",
            "username",
            "rating",
            "comment",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "product",
            "user",
            "username",
            "created_at",
        ]

    def validate_rating(self, value):
        """
        Make sure the rating is between 1 and 5.
        """

        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5 stars."
            )

        return value

    def validate_comment(self, value):
        """
        Make sure the customer actually writes a review.
        """

        if not value.strip():
            raise serializers.ValidationError(
                "Review comment cannot be empty."
            )

        return value.strip()


# ==========================================
# CATEGORY SERIALIZER
# ==========================================

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


# ==========================================
# PRODUCT SERIALIZER
# ==========================================

class ProductSerializer(serializers.ModelSerializer):

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "category",
            "category_name",
            "price",
            "description",
            "image",
            "created_at",
        ]