from django.db import models
from orders.models import Order


class Payment(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    # ==========================================
    # ORDER
    # ==========================================

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True
    )

    # ==========================================
    # CUSTOMER PAYMENT DETAILS
    # ==========================================

    phone_number = models.CharField(
        max_length=20
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # ==========================================
    # M-PESA DETAILS
    # ==========================================

    account_reference = models.CharField(
        max_length=100
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    merchant_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    checkout_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mpesa_receipt_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    result_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    result_description = models.TextField(
        blank=True,
        null=True
    )

    # ==========================================
    # PAYMENT STATUS
    # ==========================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    # ==========================================
    # TIMESTAMPS
    # ==========================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"Payment #{self.id} - "
            f"Order #{self.order.id if self.order else 'No Order'} - "
            f"KES {self.amount} - "
            f"{self.status}"
        )