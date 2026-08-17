from django.db import models
from django.conf import settings


# ==========================================
# CATEGORY
# ==========================================

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ==========================================
# PRODUCT
# ==========================================

class Product(models.Model):
    name = models.CharField(max_length=100)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="product_images/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


# ==========================================
# REVIEW
# ==========================================

class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_reviews"
    )

    rating = models.PositiveIntegerField(
        choices=[
            (1, "1 Star"),
            (2, "2 Stars"),
            (3, "3 Stars"),
            (4, "4 Stars"),
            (5, "5 Stars"),
        ]
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="unique_product_review_per_user"
            )
        ]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.rating} stars by "
            f"{self.user.username}"
        )